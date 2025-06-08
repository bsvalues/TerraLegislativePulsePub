import aiohttp
from datetime import datetime
from typing import Dict, List, Any
from .base_tracker import BaseTracker

class LegiScanTracker(BaseTracker):
    def __init__(self, api_key: str, state: str = "WA"):
        super().__init__("legiscan")
        self.api_key = api_key
        self.state = state
        self.base_url = "https://api.legiscan.com"
        
    async def fetch_data(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            params = {
                "key": self.api_key,
                "op": "getSearch",
                "state": self.state,
                "query": "property tax"
            }
            
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("searchresult", [])
                return []
    
    async def process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        processed = []
        for bill in data:
            processed.append({
                "bill_id": bill.get("bill_id"),
                "title": bill.get("title", "No Title"),
                "status": bill.get("status"),
                "last_action": bill.get("last_action"),
                "last_updated": datetime.utcnow().isoformat(),
                "source": "legiscan",
                "fetched_at": datetime.utcnow().isoformat()
            })
        return processed
    
    async def store_data(self, data: List[Dict[str, Any]]) -> None:
        # TODO: Implement database storage
        # This will be implemented when we set up the database
        pass 