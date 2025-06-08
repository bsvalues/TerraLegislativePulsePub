from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any
import logging

class BaseTracker(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"tracker.{name}")
        
    @abstractmethod
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch data from the source"""
        pass
    
    @abstractmethod
    async def process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and normalize the fetched data"""
        pass
    
    @abstractmethod
    async def store_data(self, data: List[Dict[str, Any]]) -> None:
        """Store the processed data"""
        pass
    
    async def run(self) -> None:
        """Main execution method"""
        try:
            self.logger.info(f"Starting {self.name} tracker")
            raw_data = await self.fetch_data()
            processed_data = await self.process_data(raw_data)
            await self.store_data(processed_data)
            self.logger.info(f"Completed {self.name} tracker run")
        except Exception as e:
            self.logger.error(f"Error in {self.name} tracker: {str(e)}")
            raise 