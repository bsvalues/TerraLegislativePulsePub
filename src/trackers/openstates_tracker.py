import aiohttp
from datetime import datetime
from typing import Dict, List, Any
from .base_tracker import BaseTracker

class OpenStatesTracker(BaseTracker):
    def __init__(self, api_key: str, jurisdiction: str = "Washington"):
        super().__init__("openstates")
        self.api_key = api_key
        self.jurisdiction = jurisdiction
        self.base_url = "https://v3.openstates.org"
        
    async def fetch_data(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            headers = {"X-API-Key": self.api_key}
            params = {
                "jurisdiction": self.jurisdiction,
                "q": "property tax",
                "per_page": 20
            }
            
            async with session.get(f"{self.base_url}/bills", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("results", [])
                return []
    
    async def process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        processed = []
        for bill in data:
            processed.append({
                "bill_id": bill.get("id"),
                "title": bill.get("title", "No Title"),
                "subject": ", ".join(bill.get("subjects", [])),
                "updated_at": bill.get("updated_at", datetime.utcnow().isoformat()),
                "full_text": bill.get("full_text", "No Text"),
                "source": "openstates",
                "fetched_at": datetime.utcnow().isoformat()
            })
        return processed
    
    async def store_data(self, data: List[Dict[str, Any]]) -> None:
        # TODO: Implement database storage
        # This will be implemented when we set up the database
        pass 