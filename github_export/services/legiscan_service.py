import os
import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)

def get_legiscan_api_key():
    """
    Get the LegiScan API key from environment variables
    
    Returns:
        str: The LegiScan API key
    """
    return os.environ.get('LEGISCAN_API_KEY')

def get_bill_data(bill_id):
    """
    Get detailed information about a bill from the LegiScan API
    
    Args:
        bill_id (str): The bill ID to look up
        
    Returns:
        dict: Bill data from LegiScan, or None if an error occurs
    """
    try:
        api_key = get_legiscan_api_key()
        if not api_key:
            logger.warning("LegiScan API key not found in environment variables")
            return None
        
        # Parse the bill ID to extract the bill number
        # Format is typically like "HB 1234" or "SB 5678"
        bill_parts = bill_id.split()
        if len(bill_parts) != 2:
            logger.error(f"Invalid bill ID format: {bill_id}")
            return None
        
        bill_type = bill_parts[0]  # e.g., "HB" or "SB"
        bill_number = bill_parts[1]  # e.g., "1234"
        
        # Construct the LegiScan API request
        url = "https://api.legiscan.com/"
        params = {
            "key": api_key,
            "op": "getBill",
            "state": "WA",  # Washington state
            "bill": f"{bill_type} {bill_number}"
        }
        
        # Make the API request
        response = requests.get(url, params=params)
        
        # Check for successful response
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'OK':
                return data.get('bill', {})
            else:
                logger.error(f"LegiScan API error: {data.get('alert', {}).get('message')}")
                return None
        else:
            logger.error(f"LegiScan API HTTP error: {response.status_code}")
            return None
        
    except Exception as e:
        logger.exception(f"Error retrieving bill data from LegiScan: {str(e)}")
        return None

def search_bills(keyword):
    """
    Search for bills related to a keyword
    
    Args:
        keyword (str): The keyword to search for
        
    Returns:
        list: List of bills matching the search, or empty list if an error occurs
    """
    try:
        api_key = get_legiscan_api_key()
        if not api_key:
            logger.warning("LegiScan API key not found in environment variables")
            return []
        
        # Construct the LegiScan API request
        url = "https://api.legiscan.com/"
        params = {
            "key": api_key,
            "op": "getSearchResults",
            "state": "WA",  # Washington state
            "query": keyword,
            "year": 2  # 2 = current session
        }
        
        # Make the API request
        response = requests.get(url, params=params)
        
        # Check for successful response
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'OK':
                return data.get('searchresult', [])
            else:
                logger.error(f"LegiScan API error: {data.get('alert', {}).get('message')}")
                return []
        else:
            logger.error(f"LegiScan API HTTP error: {response.status_code}")
            return []
        
    except Exception as e:
        logger.exception(f"Error searching bills from LegiScan: {str(e)}")
        return []

def get_bill_text(bill_id):
    """
    Get the full text of a bill
    
    Args:
        bill_id (str): The LegiScan bill ID (doc_id)
        
    Returns:
        str: The bill text, or None if an error occurs
    """
    try:
        api_key = get_legiscan_api_key()
        if not api_key:
            logger.warning("LegiScan API key not found in environment variables")
            return None
        
        # Construct the LegiScan API request
        url = "https://api.legiscan.com/"
        params = {
            "key": api_key,
            "op": "getBillText",
            "id": bill_id
        }
        
        # Make the API request
        response = requests.get(url, params=params)
        
        # Check for successful response
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'OK':
                return data.get('text', {}).get('doc', '')
            else:
                logger.error(f"LegiScan API error: {data.get('alert', {}).get('message')}")
                return None
        else:
            logger.error(f"LegiScan API HTTP error: {response.status_code}")
            return None
        
    except Exception as e:
        logger.exception(f"Error retrieving bill text from LegiScan: {str(e)}")
        return None
