import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Any
from .base_tracker import BaseTracker

class LocalDocumentTracker(BaseTracker):
    def __init__(self, base_url: str):
        super().__init__("local_documents")
        self.base_url = base_url
        
    async def fetch_data(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, "html.parser")
                    return self._parse_documents(soup)
                return []
    
    def _parse_documents(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        docs = []
        for div in soup.find_all("div", class_="documentItem"):
            title = div.find("a").get_text(strip=True) if div.find("a") else "No Title"
            url = div.find("a")["href"] if div.find("a") else ""
            doc_id = url.split("id=")[-1] if "id=" in url else ""
            pub_date = div.find("span", class_="pubDate").get_text(strip=True) if div.find("span", class_="pubDate") else ""
            
            docs.append({
                "doc_id": doc_id,
                "title": title,
                "url": url,
                "published_date": pub_date
            })
        return docs
    
    async def process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        processed = []
        for doc in data:
            processed.append({
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "url": doc["url"],
                "published_date": doc["published_date"],
                "source": "benton_county",
                "fetched_at": datetime.utcnow().isoformat()
            })
        return processed
    
    async def store_data(self, data: List[Dict[str, Any]]) -> None:
        # TODO: Implement database storage
        # This will be implemented when we set up the database
        pass 