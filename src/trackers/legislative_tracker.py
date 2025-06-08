from datetime import datetime
from typing import Dict, List, Any, Optional
import aiohttp
import feedparser
from bs4 import BeautifulSoup
import logging
from .base_tracker import BaseTracker

logger = logging.getLogger(__name__)

class LegislativeTracker(BaseTracker):
    def __init__(self, config: Dict[str, Any]):
        super().__init__("legislative")
        self.config = config
        self.rss_feeds = config.get("rss_feeds", [])
        self.keywords = config.get("keywords", ["property tax", "assessment", "valuation"])
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
            
            return bills
        finally:
            if self.session:
                await self.session.close()
    
    async def _fetch_rss_feeds(self) -> List[Dict[str, Any]]:
        """Fetch bills from RSS feeds"""
        bills = []
        for feed_url in self.rss_feeds:
            try:
                async with self.session.get(feed_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        for entry in feed.entries:
                            if self._is_relevant_bill(entry.title):
                                bills.append({
                                    "source": "rss",
                                    "source_id": entry.get("id", entry.get("guid")),
                                    "title": entry.title,
                                    "link": entry.link,
                                    "published": entry.get("published", ""),
                                    "summary": entry.get("summary", ""),
                                    "status": self._extract_status(entry),
                                    "last_action": self._extract_last_action(entry)
                                })
            except Exception as e:
                logger.error(f"Error fetching RSS feed {feed_url}: {str(e)}")
        return bills
    
    async def _fetch_legislative_website(self) -> List[Dict[str, Any]]:
        """Fetch bills from legislative website"""
        bills = []
        try:
            async with self.session.get(self.config["legislative_url"]) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, "html.parser")
                    
                    for bill_element in soup.find_all("div", class_="bill-item"):
                        title = bill_element.find("h3").text.strip()
                        if self._is_relevant_bill(title):
                            bills.append({
                                "source": "website",
                                "source_id": bill_element.get("data-bill-id", ""),
                                "title": title,
                                "link": bill_element.find("a")["href"],
                                "published": bill_element.find("time").text,
                                "status": bill_element.find("span", class_="status").text,
                                "last_action": bill_element.find("div", class_="last-action").text
                            })
        except Exception as e:
            logger.error(f"Error fetching legislative website: {str(e)}")
        return bills
    
    def _is_relevant_bill(self, title: str) -> bool:
        """Check if bill is relevant based on keywords"""
        return any(keyword.lower() in title.lower() for keyword in self.keywords)
    
    def _extract_status(self, entry: Dict[str, Any]) -> str:
        """Extract bill status from entry"""
        # Implement status extraction logic
        return entry.get("status", "Unknown")
    
    def _extract_last_action(self, entry: Dict[str, Any]) -> str:
        """Extract last action from entry"""
        # Implement last action extraction logic
        return entry.get("last_action", "No action recorded")
    
    async def process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and normalize bill data"""
        processed = []
        for bill in data:
            processed.append({
                **bill,
                "processed_at": datetime.utcnow().isoformat(),
                "relevance_score": self._calculate_relevance(bill),
                "categories": self._categorize_bill(bill)
            })
        return processed
    
    def _calculate_relevance(self, bill: Dict[str, Any]) -> float:
        """Calculate relevance score for bill"""
        score = 0.0
        title = bill["title"].lower()
        
        # Check keyword matches
        for keyword in self.keywords:
            if keyword.lower() in title:
                score += 0.3
        
        # Check summary matches
        if "summary" in bill:
            for keyword in self.keywords:
                if keyword.lower() in bill["summary"].lower():
                    score += 0.2
        
        return min(score, 1.0)
    
    def _categorize_bill(self, bill: Dict[str, Any]) -> List[str]:
        """Categorize bill based on content"""
        categories = []
        content = f"{bill['title']} {bill.get('summary', '')}".lower()
        
        if any(word in content for word in ["tax", "revenue", "assessment"]):
            categories.append("taxation")
        if any(word in content for word in ["property", "real estate", "land"]):
            categories.append("property")
        if any(word in content for word in ["valuation", "appraisal", "assessment"]):
            categories.append("valuation")
        
        return categories
    
    async def store_data(self, data: List[Dict[str, Any]]) -> None:
        """Store processed bill data"""
        # Implementation will be handled by the storage system
        pass 