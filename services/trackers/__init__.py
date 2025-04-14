"""
Bill Tracking Service - Trackers Package

This package contains tracker modules for different legislative data sources.
Each tracker is responsible for fetching and storing bill data from a specific source.
"""

from flask import current_app
import logging

logger = logging.getLogger(__name__)

def get_all_tracked_bills():
    """
    Retrieve all tracked bills from all tracker sources.
    
    Returns:
        list: A combined list of bills from all trackers
    """
    bills = []
    
    try:
        from .wa_legislature import get_wa_legislature_bills
        wa_bills = get_wa_legislature_bills()
        for bill in wa_bills:
            bill['source'] = 'wa_legislature'
        bills.extend(wa_bills)
    except Exception as e:
        logger.warning(f"Error getting WA Legislature bills: {str(e)}")
    
    try:
        from .openstates import get_openstates_bills
        openstates_bills = get_openstates_bills()
        for bill in openstates_bills:
            bill['source'] = 'openstates'
        bills.extend(openstates_bills)
    except Exception as e:
        logger.warning(f"Error getting OpenStates bills: {str(e)}")
    
    try:
        from .legiscan import get_legiscan_bills
        legiscan_bills = get_legiscan_bills()
        for bill in legiscan_bills:
            bill['source'] = 'legiscan'
        bills.extend(legiscan_bills)
    except Exception as e:
        logger.warning(f"Error getting LegiScan bills: {str(e)}")
    
    try:
        from .local_docs import get_local_documents
        local_docs = get_local_documents()
        for doc in local_docs:
            doc['source'] = 'local'
        bills.extend(local_docs)
    except Exception as e:
        logger.warning(f"Error getting local documents: {str(e)}")
    
    return bills

def search_bills(query):
    """
    Search for bills across all sources based on a query string.
    
    Args:
        query (str): The search query
        
    Returns:
        list: Bills matching the search query
    """
    all_bills = get_all_tracked_bills()
    
    # Simple search implementation that looks for the query in title
    query = query.lower()
    results = []
    
    for bill in all_bills:
        if query in bill.get('title', '').lower() or query in bill.get('summary', '').lower():
            results.append(bill)
    
    return results

def get_bill_by_id(bill_id, source=None):
    """
    Get a specific bill by its ID and optionally filter by source.
    
    Args:
        bill_id (str): The bill ID
        source (str, optional): The source tracker (e.g., 'wa_legislature', 'openstates')
        
    Returns:
        dict: The bill if found, None otherwise
    """
    if source == 'wa_legislature':
        from .wa_legislature import get_bill_by_id as get_wa_bill
        return get_wa_bill(bill_id)
    elif source == 'openstates':
        from .openstates import get_bill_by_id as get_os_bill
        return get_os_bill(bill_id)
    elif source == 'legiscan':
        from .legiscan import get_bill_by_id as get_ls_bill
        return get_ls_bill(bill_id)
    elif source == 'local':
        from .local_docs import get_document_by_id
        return get_document_by_id(bill_id)
    else:
        # Search all sources
        all_bills = get_all_tracked_bills()
        for bill in all_bills:
            if str(bill.get('bill_id', '')).lower() == str(bill_id).lower():
                return bill
    
    return None

def initialize_trackers():
    """
    Initialize all trackers and their databases.
    Should be called during application startup.
    """
    logger.info("Initializing legislative trackers...")
    
    try:
        from .wa_legislature import init_db as init_wa
        init_wa()
        logger.info("Initialized WA Legislature tracker")
    except Exception as e:
        logger.error(f"Error initializing WA Legislature tracker: {str(e)}")
    
    try:
        from .openstates import init_db as init_os
        init_os()
        logger.info("Initialized OpenStates tracker")
    except Exception as e:
        logger.error(f"Error initializing OpenStates tracker: {str(e)}")
    
    try:
        from .legiscan import init_db as init_ls
        init_ls()
        logger.info("Initialized LegiScan tracker")
    except Exception as e:
        logger.error(f"Error initializing LegiScan tracker: {str(e)}")
    
    try:
        from .local_docs import init_db as init_local
        init_local()
        logger.info("Initialized Local Documents tracker")
    except Exception as e:
        logger.error(f"Error initializing Local Documents tracker: {str(e)}")
    
    logger.info("All trackers initialized")