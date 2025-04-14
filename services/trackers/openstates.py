"""
Open States Tracker

This module tracks legislation from the Open States API, which provides data on
state legislative activities including bills, legislators, committees, and votes.
"""

import os
import sqlite3
import requests
import logging
from datetime import datetime
from flask import current_app

logger = logging.getLogger(__name__)

# Database file path - store in the instance folder for persistence
DB_PATH = 'instance/openstates.db'

# Open States API configuration
BASE_URL = "https://v3.openstates.org/bills"
DEFAULT_SEARCH_TERMS = [
    "property tax", 
    "assessment", 
    "valuation", 
    "assessor", 
    "property value"
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
        CREATE TABLE IF NOT EXISTS openstates_bills (
            bill_id TEXT PRIMARY KEY,
            identifier TEXT,
            title TEXT,
            subjects TEXT,
            updated_at TEXT,
            source_url TEXT,
            latest_action TEXT,
            latest_action_date TEXT,
            status TEXT,
            last_fetched TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("OpenStates database initialized")

def get_api_key():
    """Get the OpenStates API key from configuration"""
    api_key = current_app.config.get('OPENSTATES_API_KEY')
    if not api_key:
        logger.warning("OpenStates API key not configured")
    return api_key

def fetch_openstates_bills(keyword=None, limit=20):
    """
    Fetch bills from OpenStates API based on keyword
    
    Args:
        keyword (str, optional): Keyword to search for. If None, uses default terms.
        limit (int, optional): Maximum number of bills to fetch per query
    
    Returns:
        list: Bills fetched from the API
    """
    api_key = get_api_key()
    if not api_key:
        logger.error("Cannot fetch bills: OpenStates API key not configured")
        return []
    
    all_bills = []
    terms = [keyword] if keyword else DEFAULT_SEARCH_TERMS
    
    for term in terms:
        params = {
            "jurisdiction": "Washington",
            "q": term,
            "apikey": api_key,
            "per_page": limit
        }
        
        try:
            response = requests.get(BASE_URL, params=params)
            
            if response.status_code == 200:
                data = response.json()
                all_bills.extend(data.get("results", []))
                logger.info(f"Fetched {len(data.get('results', []))} bills for term '{term}'")
            else:
                logger.error(f"Error fetching bills for term '{term}': {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error during OpenStates API request for term '{term}': {str(e)}")
    
    return all_bills

def store_bill(bill):
    """
    Store or update a bill from OpenStates in the database
    
    Args:
        bill (dict): The bill data from OpenStates API
    
    Returns:
        bool: Success or failure
    """
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        
        bill_id = bill["id"]
        identifier = bill.get("identifier", "")
        title = bill.get("title", "")
        subjects = ", ".join(bill.get("subjects", []))
        updated_at = bill.get("updated_at", "")
        source_url = bill.get("source_url", "")
        
        # Extract latest action if available
        latest_action = ""
        latest_action_date = ""
        if bill.get("actions") and len(bill["actions"]) > 0:
            latest = bill["actions"][-1]
            latest_action = latest.get("description", "")
            latest_action_date = latest.get("date", "")
        
        status = bill.get("status", "")
        last_fetched = datetime.now().isoformat()
        
        try:
            c.execute('''
                INSERT INTO openstates_bills 
                (bill_id, identifier, title, subjects, updated_at, source_url, 
                latest_action, latest_action_date, status, last_fetched)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (bill_id, identifier, title, subjects, updated_at, source_url, 
                 latest_action, latest_action_date, status, last_fetched))
        except sqlite3.IntegrityError:
            # Bill already exists, update it
            c.execute('''
                UPDATE openstates_bills 
                SET identifier=?, title=?, subjects=?, updated_at=?, source_url=?,
                    latest_action=?, latest_action_date=?, status=?, last_fetched=?
                WHERE bill_id=?
            ''', (identifier, title, subjects, updated_at, source_url, 
                 latest_action, latest_action_date, status, last_fetched, bill_id))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error storing OpenStates bill: {str(e)}")
        return False

def update_all_bills():
    """
    Update all bills from OpenStates using the default search terms
    
    Returns:
        int: Number of bills updated
    """
    updated_count = 0
    
    try:
        init_db()
        bills = fetch_openstates_bills()
        
        for bill in bills:
            if store_bill(bill):
                updated_count += 1
        
        logger.info(f"Updated {updated_count} bills from OpenStates")
        return updated_count
        
    except Exception as e:
        logger.error(f"Error updating OpenStates bills: {str(e)}")
        return 0

def get_openstates_bills(limit=100):
    """
    Get all tracked bills from OpenStates
    
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
            SELECT * FROM openstates_bills
            ORDER BY updated_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = c.fetchall()
        bills = []
        
        for row in rows:
            bill = dict(row)
            bill['bill_id'] = bill['identifier']  # Ensure consistent bill_id field
            bills.append(bill)
        
        conn.close()
        return bills
        
    except Exception as e:
        logger.error(f"Error retrieving OpenStates bills: {str(e)}")
        return []

def get_bill_by_id(bill_id):
    """
    Get a specific bill by its ID
    
    Args:
        bill_id (str): The bill ID to retrieve
    
    Returns:
        dict: The bill if found, None otherwise
    """
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Try exact match on bill_id or identifier
        c.execute('''
            SELECT * FROM openstates_bills 
            WHERE bill_id = ? OR identifier = ?
        ''', (bill_id, bill_id))
        
        row = c.fetchone()
        
        if not row:
            # Try pattern match
            c.execute('''
                SELECT * FROM openstates_bills 
                WHERE bill_id LIKE ? OR identifier LIKE ?
            ''', (f'%{bill_id}%', f'%{bill_id}%'))
            row = c.fetchone()
        
        if row:
            bill = dict(row)
            conn.close()
            return bill
        
        conn.close()
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving OpenStates bill by ID: {str(e)}")
        return None

def search_bills(query, limit=50):
    """
    Search for bills containing the query in title or subjects
    
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
            SELECT * FROM openstates_bills 
            WHERE title LIKE ? OR subjects LIKE ?
            ORDER BY updated_at DESC
            LIMIT ?
        ''', (like_query, like_query, limit))
        
        rows = c.fetchall()
        bills = [dict(row) for row in rows]
        
        conn.close()
        return bills
        
    except Exception as e:
        logger.error(f"Error searching OpenStates bills: {str(e)}")
        return []

if __name__ == "__main__":
    # Configure logging when run as a standalone script
    logging.basicConfig(level=logging.INFO)
    update_all_bills()