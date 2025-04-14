"""
LegiScan Tracker

This module tracks legislation from the LegiScan API, which provides access to 
legislative data across all 50 states. The free tier has usage limits, so this
implementation is designed to be conservative with API calls.
"""

import os
import sqlite3
import requests
import logging
from datetime import datetime
from flask import current_app

logger = logging.getLogger(__name__)

# Database file path - store in the instance folder for persistence
DB_PATH = 'instance/legiscan.db'

# LegiScan API configuration
BASE_URL = "https://api.legiscan.com/"
DEFAULT_SEARCH_TERMS = [
    "property tax", 
    "assessment", 
    "valuation", 
    "assessor"
]

def get_db_path():
    """Get the full path to the database file"""
    # Ensure instance directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return DB_PATH

def init_db():
    """Initialize the database schema"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS legiscan_bills (
            bill_id INTEGER PRIMARY KEY,
            state TEXT,
            bill_number TEXT,
            title TEXT,
            description TEXT,
            status TEXT,
            last_action TEXT,
            last_action_date TEXT,
            url TEXT,
            last_fetched TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("LegiScan database initialized")

def get_api_key():
    """Get the LegiScan API key from configuration"""
    api_key = current_app.config.get('LEGISCAN_API_KEY')
    if not api_key:
        logger.warning("LegiScan API key not configured")
    return api_key

def fetch_legiscan_bills(state="WA", keyword=None, limit=50):
    """
    Fetch bills from LegiScan API based on keyword
    
    Args:
        state (str, optional): State code (default: WA for Washington)
        keyword (str, optional): Keyword to search for. If None, uses default terms.
        limit (int, optional): Maximum number of bills to fetch
    
    Returns:
        list: Bills fetched from the API
    """
    api_key = get_api_key()
    if not api_key:
        logger.error("Cannot fetch bills: LegiScan API key not configured")
        return []
    
    all_bills = []
    terms = [keyword] if keyword else DEFAULT_SEARCH_TERMS
    
    for term in terms:
        params = {
            "key": api_key,
            "op": "getSearch",
            "state": state,
            "query": term,
            "year": 0  # Current session
        }
        
        try:
            response = requests.get(BASE_URL, params=params)
            
            if response.status_code == 200:
                data = response.json()
                search_result = data.get("searchresult", {})
                
                # LegiScan returns a dictionary with bill_ids as keys
                for key, bill in search_result.items():
                    if key != "summary":  # Skip the summary entry
                        all_bills.append(bill)
                
                logger.info(f"Fetched {len(all_bills)} bills for term '{term}'")
                
                # Respect API limits by only taking a few bills per term
                if len(all_bills) >= limit:
                    break
                    
            else:
                logger.error(f"Error fetching bills for term '{term}': {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error during LegiScan API request for term '{term}': {str(e)}")
    
    return all_bills[:limit]  # Respect the limit

def store_legiscan_bill(bill):
    """
    Store or update a bill from LegiScan in the database
    
    Args:
        bill (dict): The bill data from LegiScan API
    
    Returns:
        bool: Success or failure
    """
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        
        bill_id = bill.get("bill_id")
        state = bill.get("state")
        bill_number = bill.get("bill_number", "")
        title = bill.get("title", "")
        description = bill.get("description", "")
        status = bill.get("status", "")
        last_action = bill.get("last_action", "")
        last_action_date = bill.get("last_action_date", "")
        url = bill.get("url", "")
        last_fetched = datetime.now().isoformat()
        
        try:
            c.execute('''
                INSERT INTO legiscan_bills 
                (bill_id, state, bill_number, title, description, status, 
                last_action, last_action_date, url, last_fetched)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (bill_id, state, bill_number, title, description, status, 
                 last_action, last_action_date, url, last_fetched))
        except sqlite3.IntegrityError:
            # Bill already exists, update it
            c.execute('''
                UPDATE legiscan_bills 
                SET state=?, bill_number=?, title=?, description=?, status=?, 
                    last_action=?, last_action_date=?, url=?, last_fetched=?
                WHERE bill_id=?
            ''', (state, bill_number, title, description, status, 
                 last_action, last_action_date, url, last_fetched, bill_id))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error storing LegiScan bill: {str(e)}")
        return False

def update_all_bills(state="WA"):
    """
    Update all bills from LegiScan using the default search terms
    
    Args:
        state (str, optional): State code (default: WA for Washington)
    
    Returns:
        int: Number of bills updated
    """
    updated_count = 0
    
    try:
        init_db()
        bills = fetch_legiscan_bills(state=state)
        
        for bill in bills:
            if store_legiscan_bill(bill):
                updated_count += 1
        
        logger.info(f"Updated {updated_count} bills from LegiScan")
        return updated_count
        
    except Exception as e:
        logger.error(f"Error updating LegiScan bills: {str(e)}")
        return 0

def get_legiscan_bills(limit=100):
    """
    Get all tracked bills from LegiScan
    
    Args:
        limit (int, optional): Maximum number of bills to return
    
    Returns:
        list: A list of bill dictionaries
    """
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('''
            SELECT * FROM legiscan_bills
            ORDER BY last_action_date DESC
            LIMIT ?
        ''', (limit,))
        
        rows = c.fetchall()
        bills = []
        
        for row in rows:
            bill = dict(row)
            bill['bill_id'] = f"{bill['state']} {bill['bill_number']}"  # Ensure consistent bill_id field
            bills.append(bill)
        
        conn.close()
        return bills
        
    except Exception as e:
        logger.error(f"Error retrieving LegiScan bills: {str(e)}")
        return []

def get_bill_by_id(bill_id):
    """
    Get a specific bill by its ID
    
    Args:
        bill_id (str): The bill ID to retrieve (could be LegiScan ID or bill number)
    
    Returns:
        dict: The bill if found, None otherwise
    """
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Try as numeric ID first
        try:
            numeric_id = int(bill_id)
            c.execute('SELECT * FROM legiscan_bills WHERE bill_id = ?', (numeric_id,))
            row = c.fetchone()
            if row:
                bill = dict(row)
                conn.close()
                return bill
        except ValueError:
            pass  # Not a numeric ID, continue to next checks
        
        # Try as bill number
        c.execute('SELECT * FROM legiscan_bills WHERE bill_number = ?', (bill_id,))
        row = c.fetchone()
        
        if not row:
            # Try pattern match
            c.execute('SELECT * FROM legiscan_bills WHERE bill_number LIKE ?', (f'%{bill_id}%',))
            row = c.fetchone()
        
        if row:
            bill = dict(row)
            conn.close()
            return bill
        
        conn.close()
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving LegiScan bill by ID: {str(e)}")
        return None

def search_bills(query, limit=50):
    """
    Search for bills containing the query in title, description, or bill number
    
    Args:
        query (str): The search query
        limit (int, optional): Maximum number of results
    
    Returns:
        list: Matching bills
    """
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        like_query = f'%{query}%'
        c.execute('''
            SELECT * FROM legiscan_bills 
            WHERE title LIKE ? OR description LIKE ? OR bill_number LIKE ?
            ORDER BY last_action_date DESC
            LIMIT ?
        ''', (like_query, like_query, like_query, limit))
        
        rows = c.fetchall()
        bills = [dict(row) for row in rows]
        
        conn.close()
        return bills
        
    except Exception as e:
        logger.error(f"Error searching LegiScan bills: {str(e)}")
        return []

if __name__ == "__main__":
    # Configure logging when run as a standalone script
    logging.basicConfig(level=logging.INFO)
    update_all_bills()