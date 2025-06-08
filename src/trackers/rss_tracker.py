import aiohttp
import feedparser
from datetime import datetime
from typing import Dict, List, Any
from .base_tracker import BaseTracker

class RSSLegislatureTracker(BaseTracker):
    def __init__(self, feed_urls: List[str]):
        super().__init__("rss_legislature")
        self.feed_urls = feed_urls
        
    async def fetch_data(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            all_entries = []
            for url in self.feed_urls:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        all_entries.extend(feed.entries)
            return all_entries
    
    async def process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        processed = []
        for entry in data:
            processed.append({
                "guid": entry.get("id", entry.get("guid")),
                "title": entry.get("title", "No Title"),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "source": "washington_legislature",
                "fetched_at": datetime.utcnow().isoformat()
            })
        return processed
    
    async def store_data(self, data: List[Dict[str, Any]]) -> None:
        # TODO: Implement database storage
        # This will be implemented when we set up the database
        pass 