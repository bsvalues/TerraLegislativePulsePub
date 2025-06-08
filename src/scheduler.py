import asyncio
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Type
from trackers.base_tracker import BaseTracker
from trackers.rss_tracker import RSSLegislatureTracker
from trackers.openstates_tracker import OpenStatesTracker
from trackers.legiscan_tracker import LegiScanTracker
from trackers.local_tracker import LocalDocumentTracker
from models.base import SessionLocal

logger = logging.getLogger(__name__)

class TrackerScheduler:
    def __init__(self):
        self.trackers: Dict[str, BaseTracker] = {}
        self.schedules: Dict[str, timedelta] = {}
        self.running = False
    
    def register_tracker(self, tracker: BaseTracker, interval: timedelta):
        """Register a tracker with its update interval"""
        self.trackers[tracker.name] = tracker
        self.schedules[tracker.name] = interval
    
    async def run_tracker(self, tracker_name: str):
        """Run a single tracker"""
        tracker = self.trackers[tracker_name]
        try:
            logger.info(f"Running tracker: {tracker_name}")
            await tracker.run()
            logger.info(f"Completed tracker: {tracker_name}")
        except Exception as e:
            logger.error(f"Error in tracker {tracker_name}: {str(e)}")
    
    async def schedule_tracker(self, tracker_name: str):
        """Schedule a tracker to run at its interval"""
        while self.running:
            await self.run_tracker(tracker_name)
            await asyncio.sleep(self.schedules[tracker_name].total_seconds())
    
    async def start(self):
        """Start all trackers"""
        self.running = True
        tasks = []
        for tracker_name in self.trackers:
            tasks.append(asyncio.create_task(self.schedule_tracker(tracker_name)))
        await asyncio.gather(*tasks)
    
    def stop(self):
        """Stop all trackers"""
        self.running = False

def create_scheduler(config: dict) -> TrackerScheduler:
    """Create and configure the scheduler with trackers"""
    scheduler = TrackerScheduler()
    
    # Configure RSS tracker
    rss_tracker = RSSLegislatureTracker(config["rss_feeds"])
    scheduler.register_tracker(rss_tracker, timedelta(minutes=30))
    
    # Configure OpenStates tracker
    openstates_tracker = OpenStatesTracker(
        config["openstates_api_key"],
        config.get("openstates_jurisdiction", "Washington")
    )
    scheduler.register_tracker(openstates_tracker, timedelta(hours=1))
    
    # Configure LegiScan tracker
    legiscan_tracker = LegiScanTracker(
        config["legiscan_api_key"],
        config.get("legiscan_state", "WA")
    )
    scheduler.register_tracker(legiscan_tracker, timedelta(hours=2))
    
    # Configure Local Document tracker
    local_tracker = LocalDocumentTracker(config["local_docs_url"])
    scheduler.register_tracker(local_tracker, timedelta(hours=4))
    
    return scheduler

async def run_scheduler(config: dict):
    """Run the scheduler with the given configuration"""
    scheduler = create_scheduler(config)
    try:
        await scheduler.start()
    except KeyboardInterrupt:
        scheduler.stop()
        logger.info("Scheduler stopped") 