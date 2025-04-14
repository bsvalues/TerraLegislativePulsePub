import os
import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)

def get_openstates_api_key():
    """
    Get the OpenStates API key from environment variables
    
    Returns:
        str: The OpenStates API key
    """
    return os.environ.get('OPENSTATES_API_KEY')

def get_legislative_data(bill_id):
    """
    Get information about a bill from the OpenStates API
    
    Args:
        bill_id (str): The bill ID to look up
        
    Returns:
        dict: Bill data from OpenStates, or None if an error occurs
    """
    try:
        api_key = get_openstates_api_key()
        if not api_key:
            logger.warning("OpenStates API key not found in environment variables")
            return None
        
        # Parse the bill ID to extract components
        # Format is typically like "HB 1234" or "SB 5678"
        bill_parts = bill_id.split()
        if len(bill_parts) != 2:
            logger.error(f"Invalid bill ID format: {bill_id}")
            return None
        
        bill_type = bill_parts[0].lower()  # e.g., "hb" or "sb"
        bill_number = bill_parts[1]  # e.g., "1234"
        
        # Construct the OpenStates API request
        url = f"https://v3.openstates.org/bills"
        params = {
            "jurisdiction": "Washington",
            "identifier": bill_id,
            "apikey": api_key
        }
        headers = {
            "Accept": "application/json"
        }
        
        # Make the API request
        response = requests.get(url, params=params, headers=headers)
        
        # Check for successful response
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if results:
                return results[0]
            else:
                logger.warning(f"No results found for bill {bill_id}")
                return None
        else:
            logger.error(f"OpenStates API HTTP error: {response.status_code}")
            return None
        
    except Exception as e:
        logger.exception(f"Error retrieving legislative data from OpenStates: {str(e)}")
        return None

def search_bills(query, state="WA"):
    """
    Search for bills in the OpenStates API
    
    Args:
        query (str): The search query
        state (str): The state to search in (default: WA)
        
    Returns:
        list: List of bills matching the search, or empty list if an error occurs
    """
    try:
        api_key = get_openstates_api_key()
        if not api_key:
            logger.warning("OpenStates API key not found in environment variables")
            return []
        
        # Construct the OpenStates API request
        url = f"https://v3.openstates.org/bills"
        params = {
            "jurisdiction": state,
            "query": query,
            "apikey": api_key
        }
        headers = {
            "Accept": "application/json"
        }
        
        # Make the API request
        response = requests.get(url, params=params, headers=headers)
        
        # Check for successful response
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        else:
            logger.error(f"OpenStates API HTTP error: {response.status_code}")
            return []
        
    except Exception as e:
        logger.exception(f"Error searching bills from OpenStates: {str(e)}")
        return []

def get_recent_legislative_updates(state="WA", limit=10):
    """
    Get recent legislative updates from OpenStates
    
    Args:
        state (str): The state to get updates for (default: WA)
        limit (int): The maximum number of updates to retrieve
        
    Returns:
        list: List of recent legislative updates, or empty list if an error occurs
    """
    try:
        api_key = get_openstates_api_key()
        if not api_key:
            logger.warning("OpenStates API key not found in environment variables")
            return []
        
        # Construct the OpenStates API request
        url = f"https://v3.openstates.org/bills"
        params = {
            "jurisdiction": state,
            "sort": "updated_desc",
            "per_page": limit,
            "apikey": api_key
        }
        headers = {
            "Accept": "application/json"
        }
        
        # Make the API request
        response = requests.get(url, params=params, headers=headers)
        
        # Check for successful response
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        else:
            logger.error(f"OpenStates API HTTP error: {response.status_code}")
            return []
        
    except Exception as e:
        logger.exception(f"Error retrieving recent legislative updates from OpenStates: {str(e)}")
        return []
