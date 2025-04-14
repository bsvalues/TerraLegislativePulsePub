"""
Legislative Tracking Scheduler

This script schedules regular updates of the legislative trackers to keep the 
bills database up to date. It can be run as a standalone process or integrated
with the main application.
"""

import time
import logging
import threading
import schedule
from datetime import datetime
from flask import Flask, current_app
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create a minimal Flask app for the scheduler context"""
    app = Flask(__name__)
    
    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Configure API keys from environment
    app.config['LEGISCAN_API_KEY'] = os.environ.get('LEGISCAN_API_KEY')
    app.config['OPENSTATES_API_KEY'] = os.environ.get('OPENSTATES_API_KEY')
    
    return app

def update_wa_legislature_tracker():
    """Update the Washington State Legislature tracker"""
    try:
        logger.info("Updating WA Legislature tracker...")
        from services.trackers.wa_legislature import fetch_and_store
        bills_updated = fetch_and_store()
        logger.info(f"Updated {bills_updated} bills from WA Legislature tracker")
        return bills_updated
    except Exception as e:
        logger.error(f"Error updating WA Legislature tracker: {str(e)}")
        return 0

def update_openstates_tracker():
    """Update the OpenStates tracker"""
    try:
        logger.info("Updating OpenStates tracker...")
        from services.trackers.openstates import update_all_bills
        bills_updated = update_all_bills()
        logger.info(f"Updated {bills_updated} bills from OpenStates tracker")
        return bills_updated
    except Exception as e:
        logger.error(f"Error updating OpenStates tracker: {str(e)}")
        return 0

def update_legiscan_tracker():
    """Update the LegiScan tracker"""
    try:
        logger.info("Updating LegiScan tracker...")
        from services.trackers.legiscan import update_all_bills
        bills_updated = update_all_bills()
        logger.info(f"Updated {bills_updated} bills from LegiScan tracker")
        return bills_updated
    except Exception as e:
        logger.error(f"Error updating LegiScan tracker: {str(e)}")
        return 0

def update_local_docs_tracker():
    """Update the local documents tracker"""
    try:
        logger.info("Updating Local Documents tracker...")
        from services.trackers.local_docs import update_all_documents
        docs_updated = update_all_documents()
        logger.info(f"Updated {docs_updated} documents from Local Documents tracker")
        return docs_updated
    except Exception as e:
        logger.error(f"Error updating Local Documents tracker: {str(e)}")
        return 0

def update_all_trackers():
    """Update all legislative trackers"""
    logger.info("Starting scheduled update of all trackers...")
    app = create_app()
    
    with app.app_context():
        wa_count = update_wa_legislature_tracker()
        time.sleep(1)  # Pause to avoid rate limits
        
        openstates_count = update_openstates_tracker()
        time.sleep(1)  # Pause to avoid rate limits
        
        legiscan_count = update_legiscan_tracker()
        time.sleep(1)  # Pause to avoid rate limits
        
        local_count = update_local_docs_tracker()
        
        total_updated = wa_count + openstates_count + legiscan_count + local_count
        logger.info(f"Completed tracker updates. Total items updated: {total_updated}")
        
        # Update last_updated time in a database or file
        update_time = datetime.now().isoformat()
        logger.info(f"Trackers last updated at: {update_time}")

def run_scheduler():
    """Run the scheduler as a background thread"""
    logger.info("Starting legislative tracker scheduler...")
    
    # Schedule updates at different intervals to distribute the load
    schedule.every().day.at("02:00").do(update_all_trackers)  # Daily update at 2 AM
    schedule.every().monday.at("06:00").do(update_wa_legislature_tracker)  # Monday morning
    schedule.every().wednesday.at("06:00").do(update_openstates_tracker)  # Wednesday morning
    schedule.every().friday.at("06:00").do(update_legiscan_tracker)  # Friday morning
    
    # For testing - uncomment to run immediately
    # update_all_trackers()
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def start_scheduler_thread():
    """Start the scheduler in a background thread"""
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True  # Thread will exit when main thread exits
    scheduler_thread.start()
    logger.info("Legislative tracker scheduler thread started")
    return scheduler_thread

if __name__ == "__main__":
    logger.info("Running legislative tracker scheduler as standalone process")
    run_scheduler()