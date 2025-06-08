from datetime import datetime
from typing import Dict, List, Any, Optional
import aiohttp
import feedparser
from bs4 import BeautifulSoup
import logging
import re
from .base_tracker import BaseTracker

logger = logging.getLogger(__name__)

class EnhancedLegislativeTracker(BaseTracker):
    def __init__(self, config: Dict[str, Any]):
        super().__init__("enhanced_legislative")
        self.config = config
        self.rss_feeds = config.get("rss_feeds", [])
        self.keywords = config.get("keywords", ["property tax", "assessment", "valuation"])
        self.committee_urls = config.get("committee_urls", {})
        self.hearing_urls = config.get("hearing_urls", {})
        self.fiscal_urls = config.get("fiscal_urls", {})
        self.session = None
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch data from multiple sources"""
        self.session = aiohttp.ClientSession()
        try:
            bills = []
            # Fetch from RSS feeds
            rss_bills = await self._fetch_rss_feeds()
            bills.extend(rss_bills)
            
            # Fetch from legislative website
            web_bills = await self._fetch_legislative_website()
            bills.extend(web_bills)
            
            # Fetch committee information
            committee_data = await self._fetch_committee_data()
            self._enrich_bills_with_committee_data(bills, committee_data)
            
            # Fetch hearing information
            hearing_data = await self._fetch_hearing_data()
            self._enrich_bills_with_hearing_data(bills, hearing_data)
            
            # Fetch fiscal notes
            fiscal_data = await self._fetch_fiscal_data()
            self._enrich_bills_with_fiscal_data(bills, fiscal_data)
            
            return bills
        finally:
            if self.session:
                await self.session.close()
    
    async def _fetch_committee_data(self) -> Dict[str, Any]:
        """Fetch committee meeting information"""
        committee_data = {}
        for committee, url in self.committee_urls.items():
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, "html.parser")
                        committee_data[committee] = self._parse_committee_page(soup)
            except Exception as e:
                logger.error(f"Error fetching committee data for {committee}: {str(e)}")
        return committee_data
    
    async def _fetch_hearing_data(self) -> Dict[str, Any]:
        """Fetch public hearing information"""
        hearing_data = {}
        for hearing_type, url in self.hearing_urls.items():
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, "html.parser")
                        hearing_data[hearing_type] = self._parse_hearing_page(soup)
            except Exception as e:
                logger.error(f"Error fetching hearing data for {hearing_type}: {str(e)}")
        return hearing_data
    
    async def _fetch_fiscal_data(self) -> Dict[str, Any]:
        """Fetch fiscal notes and analysis"""
        fiscal_data = {}
        for fiscal_type, url in self.fiscal_urls.items():
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, "html.parser")
                        fiscal_data[fiscal_type] = self._parse_fiscal_page(soup)
            except Exception as e:
                logger.error(f"Error fetching fiscal data for {fiscal_type}: {str(e)}")
        return fiscal_data
    
    def _parse_committee_page(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parse committee meeting page"""
        meetings = []
        for meeting in soup.find_all("div", class_="meeting-item"):
            meetings.append({
                "date": meeting.find("time").text,
                "bills": [bill.text for bill in meeting.find_all("a", class_="bill-link")],
                "minutes_url": meeting.find("a", class_="minutes-link")["href"] if meeting.find("a", class_="minutes-link") else None,
                "video_url": meeting.find("a", class_="video-link")["href"] if meeting.find("a", class_="video-link") else None
            })
        return {"meetings": meetings}
    
    def _parse_hearing_page(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parse public hearing page"""
        hearings = []
        for hearing in soup.find_all("div", class_="hearing-item"):
            hearings.append({
                "date": hearing.find("time").text,
                "bills": [bill.text for bill in hearing.find_all("a", class_="bill-link")],
                "location": hearing.find("div", class_="location").text,
                "transcript_url": hearing.find("a", class_="transcript-link")["href"] if hearing.find("a", class_="transcript-link") else None
            })
        return {"hearings": hearings}
    
    def _parse_fiscal_page(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parse fiscal notes page"""
        fiscal_notes = []
        for note in soup.find_all("div", class_="fiscal-note"):
            fiscal_notes.append({
                "bill_id": note.find("div", class_="bill-id").text,
                "impact": note.find("div", class_="impact").text,
                "amount": self._extract_fiscal_amount(note.find("div", class_="amount").text),
                "analysis_url": note.find("a", class_="analysis-link")["href"] if note.find("a", class_="analysis-link") else None
            })
        return {"fiscal_notes": fiscal_notes}
    
    def _extract_fiscal_amount(self, amount_text: str) -> float:
        """Extract fiscal amount from text"""
        try:
            # Remove currency symbols and commas, then convert to float
            return float(re.sub(r'[^\d.-]', '', amount_text))
        except (ValueError, TypeError):
            return 0.0
    
    def _enrich_bills_with_committee_data(self, bills: List[Dict[str, Any]], committee_data: Dict[str, Any]):
        """Enrich bills with committee information"""
        for bill in bills:
            bill["committee_activity"] = []
            for committee, data in committee_data.items():
                for meeting in data["meetings"]:
                    if bill["source_id"] in meeting["bills"]:
                        bill["committee_activity"].append({
                            "committee": committee,
                            "date": meeting["date"],
                            "minutes_url": meeting["minutes_url"],
                            "video_url": meeting["video_url"]
                        })
    
    def _enrich_bills_with_hearing_data(self, bills: List[Dict[str, Any]], hearing_data: Dict[str, Any]):
        """Enrich bills with hearing information"""
        for bill in bills:
            bill["hearings"] = []
            for hearing_type, data in hearing_data.items():
                for hearing in data["hearings"]:
                    if bill["source_id"] in hearing["bills"]:
                        bill["hearings"].append({
                            "type": hearing_type,
                            "date": hearing["date"],
                            "location": hearing["location"],
                            "transcript_url": hearing["transcript_url"]
                        })
    
    def _enrich_bills_with_fiscal_data(self, bills: List[Dict[str, Any]], fiscal_data: Dict[str, Any]):
        """Enrich bills with fiscal information"""
        for bill in bills:
            bill["fiscal_impact"] = []
            for fiscal_type, data in fiscal_data.items():
                for note in data["fiscal_notes"]:
                    if note["bill_id"] == bill["source_id"]:
                        bill["fiscal_impact"].append({
                            "type": fiscal_type,
                            "impact": note["impact"],
                            "amount": note["amount"],
                            "analysis_url": note["analysis_url"]
                        })
    
    async def process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and normalize bill data"""
        processed = []
        for bill in data:
            processed.append({
                **bill,
                "processed_at": datetime.utcnow().isoformat(),
                "relevance_score": self._calculate_relevance(bill),
                "categories": self._categorize_bill(bill),
                "impact_score": self._calculate_impact_score(bill)
            })
        return processed
    
    def _calculate_impact_score(self, bill: Dict[str, Any]) -> float:
        """Calculate impact score based on various factors"""
        score = 0.0
        
        # Committee activity impact
        score += len(bill.get("committee_activity", [])) * 0.1
        
        # Hearing impact
        score += len(bill.get("hearings", [])) * 0.15
        
        # Fiscal impact
        fiscal_impact = bill.get("fiscal_impact", [])
        if fiscal_impact:
            total_amount = sum(impact["amount"] for impact in fiscal_impact)
            score += min(total_amount / 1000000, 0.3)  # Cap at 0.3 for fiscal impact
        
        # Sponsor impact (if available)
        if "sponsors" in bill:
            score += min(len(bill["sponsors"]) * 0.05, 0.2)  # Cap at 0.2 for sponsor impact
        
        return min(score, 1.0)
    
    def _calculate_relevance(self, bill: Dict[str, Any]) -> float:
        """Calculate relevance score for bill"""
        score = 0.0
        title = bill["title"].lower()
        summary = bill.get("summary", "").lower()
        
        # Check keyword matches in title
        for keyword in self.keywords:
            if keyword.lower() in title:
                score += 0.3
        
        # Check keyword matches in summary
        for keyword in self.keywords:
            if keyword.lower() in summary:
                score += 0.2
        
        # Check committee relevance
        if "committee_activity" in bill:
            score += min(len(bill["committee_activity"]) * 0.1, 0.2)
        
        # Check hearing relevance
        if "hearings" in bill:
            score += min(len(bill["hearings"]) * 0.1, 0.2)
        
        return min(score, 1.0)
    
    def _categorize_bill(self, bill: Dict[str, Any]) -> List[str]:
        """Categorize bill based on content"""
        categories = []
        content = f"{bill['title']} {bill.get('summary', '')}".lower()
        
        # Basic categories
        if any(word in content for word in ["tax", "revenue", "assessment"]):
            categories.append("taxation")
        if any(word in content for word in ["property", "real estate", "land"]):
            categories.append("property")
        if any(word in content for word in ["valuation", "appraisal", "assessment"]):
            categories.append("valuation")
        
        # Committee-based categories
        if "committee_activity" in bill:
            for activity in bill["committee_activity"]:
                committee = activity["committee"].lower()
                if "finance" in committee or "revenue" in committee:
                    categories.append("finance")
                if "local" in committee or "county" in committee:
                    categories.append("local_government")
        
        # Fiscal impact categories
        if "fiscal_impact" in bill:
            for impact in bill["fiscal_impact"]:
                if impact["amount"] > 0:
                    categories.append("revenue_impact")
                if impact["amount"] < 0:
                    categories.append("expenditure_impact")
        
        return list(set(categories))  # Remove duplicates
    
    async def store_data(self, data: List[Dict[str, Any]]) -> None:
        """Store processed bill data"""
        # Implementation will be handled by the storage system
        pass 