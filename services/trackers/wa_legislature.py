"""
Washington State Legislature Tracker

This module tracks legislation from the Washington State Legislature using their RSS feeds.
"""

import os
import feedparser
import sqlite3
import time
import logging
from datetime import datetime
from flask import current_app

logger = logging.getLogger(__name__)

# Database file path - store in the instance folder for persistence
DB_PATH = 'instance/state_legislation.db'

# Define RSS feed URLs for tracking relevant bills
DEFAULT_RSS_FEEDS = [
    "https://leg.wa.gov/bills-meetings-and-session/bills/rss.xml",  # General feed
    # Add more specific feeds as needed
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
        CREATE TABLE IF NOT EXISTS wa_bills (
            guid TEXT PRIMARY KEY,
            bill_id TEXT,
            title TEXT,
            link TEXT,
            published TEXT,
            summary TEXT,
            last_updated TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("WA Legislature database initialized")

def fetch_and_store(feed_url=None):
    """
    Fetch and store bills from a Washington State Legislature RSS feed
    
    Args:
        feed_url (str, optional): The feed URL to fetch. If None, uses all default feeds.
    
    Returns:
        int: Number of new or updated bills
    """
    feed_urls = [feed_url] if feed_url else DEFAULT_RSS_FEEDS
    updated_count = 0
    
    for url in feed_urls:
        try:
            d = feedparser.parse(url)
            conn = sqlite3.connect(get_db_path())
            c = conn.cursor()
            
            for entry in d.entries:
                # Extract bill ID from title (e.g., "HB 1234: Description")
                title_parts = entry.get("title", "").split(":", 1)
                bill_id = title_parts[0].strip() if len(title_parts) > 0 else "Unknown"
                
                guid = entry.get("id", entry.get("guid", ""))
                title = entry.get("title", "No Title")
                link = entry.get("link", "")
                published = entry.get("published", "")
                summary = entry.get("summary", "")
                last_updated = datetime.now().isoformat()
                
                try:
                    c.execute('''
                        INSERT INTO wa_bills (guid, bill_id, title, link, published, summary, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (guid, bill_id, title, link, published, summary, last_updated))
                    updated_count += 1
                except sqlite3.IntegrityError:
                    # Bill already exists, update
                    c.execute('''
                        UPDATE wa_bills 
                        SET bill_id=?, title=?, link=?, published=?, summary=?, last_updated=?
                        WHERE guid=?
                    ''', (bill_id, title, link, published, summary, last_updated, guid))
                    updated_count += 1
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed {url}: {str(e)}")
    
    logger.info(f"Updated {updated_count} bills from WA Legislature")
    return updated_count

def get_wa_legislature_bills(limit=100):
    """
    Get all tracked bills from the Washington State Legislature
    
    Args:
        limit (int, optional): Maximum number of bills to return
    
    Returns:
        list: A list of bill dictionaries
    """
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row  # Return results as dictionaries
        c = conn.cursor()
        
        c.execute('''
            SELECT * FROM wa_bills
            ORDER BY published DESC
            LIMIT ?
        ''', (limit,))
        
        rows = c.fetchall()
        bills = []
        
        for row in rows:
            bill = dict(row)
            bill['bill_id'] = bill['bill_id']  # Ensure consistent bill_id field
            bills.append(bill)
        
        conn.close()
        return bills
        
    except Exception as e:
        logger.error(f"Error retrieving WA Legislature bills: {str(e)}")
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
        
        # Try exact match first
        c.execute('SELECT * FROM wa_bills WHERE bill_id = ?', (bill_id,))
        row = c.fetchone()
        
        if not row:
            # Try pattern match (e.g., search for "1234" in "HB 1234")
            c.execute('SELECT * FROM wa_bills WHERE bill_id LIKE ?', (f'%{bill_id}%',))
            row = c.fetchone()
        
        if row:
            bill = dict(row)
            conn.close()
            return bill
        
        conn.close()
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving WA Legislature bill by ID: {str(e)}")
        return None

def search_bills(query, limit=50):
    """
    Search for bills containing the query in title or summary
    
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
            SELECT * FROM wa_bills 
            WHERE title LIKE ? OR summary LIKE ?
            ORDER BY published DESC
            LIMIT ?
        ''', (like_query, like_query, limit))
        
        rows = c.fetchall()
        bills = [dict(row) for row in rows]
        
        conn.close()
        return bills
        
    except Exception as e:
        logger.error(f"Error searching WA Legislature bills: {str(e)}")
        return []

def run_rss_tracker(interval=1800):
    """
    Run the RSS tracker continuously with a sleep interval
    
    Args:
        interval (int, optional): Sleep interval in seconds between updates
    """
    logger.info("Starting WA Legislature RSS tracker")
    init_db()
    
    try:
        while True:
            fetch_and_store()
            logger.info(f"Feeds updated. Sleeping for {interval} seconds...")
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("WA Legislature tracker stopped")

if __name__ == "__main__":
    # Configure logging when run as a standalone script
    logging.basicConfig(level=logging.INFO)
    run_rss_tracker()