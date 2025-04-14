"""
Trackers Package

This package provides functionality for tracking bills from various sources.
"""

import logging
from typing import List, Dict, Any

from flask import current_app

logger = logging.getLogger(__name__)

# Import the various trackers
from services.trackers import (
    wa_legislature,
    openstates,
    legiscan,
    local_docs
)

def initialize_trackers():
    """Initialize all legislative trackers"""
    logger.info("Initializing legislative trackers")
    
    # Initialize each tracker's database
    wa_legislature.init_db()
    openstates.init_db()
    legiscan.init_db()
    local_docs.init_db()
    
    logger.info("All legislative trackers initialized")

def update_all_bills() -> Dict[str, int]:
    """
    Update bills from all sources
    
    Returns:
        Dict[str, int]: The number of bills added or updated by each source
    """
    logger.info("Updating all legislative sources")
    
    results = {
        "wa_legislature": 0,
        "openstates": 0, 
        "legiscan": 0,
        "local_docs": 0
    }
    
    try:
        # Update each source
        results["wa_legislature"] = wa_legislature.fetch_and_store()
        results["openstates"] = openstates.fetch_and_store()
        results["legiscan"] = legiscan.fetch_and_store()
        results["local_docs"] = local_docs.fetch_and_store()
        
        total = sum(results.values())
        logger.info(f"Updated {total} bills from all sources")
        
    except Exception as e:
        logger.exception(f"Error updating bills: {str(e)}")
    
    return results

def update_all_documents() -> Dict[str, int]:
    """
    Update local documents
    
    Returns:
        Dict[str, int]: The number of documents added or updated
    """
    logger.info("Updating local documents")
    
    results = {
        "local_docs": 0
    }
    
    try:
        # Update local documents
        results["local_docs"] = local_docs.fetch_and_store()
        
        logger.info(f"Updated {results['local_docs']} documents")
        
    except Exception as e:
        logger.exception(f"Error updating documents: {str(e)}")
    
    return results