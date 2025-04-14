"""
Local Documents Tracker

This module tracks local documents from the Benton County resources,
using web scraping techniques to extract relevant documentation.
"""

import os
import sqlite3
import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from flask import current_app

logger = logging.getLogger(__name__)

# Database file path - store in the instance folder for persistence
DB_PATH = 'instance/benton_local.db'

# Local document sources
DEFAULT_DOCUMENT_URLS = [
    "https://www.co.benton.wa.us/pview.aspx?id=1963&catid=45",  # Assessor's resources example URL
    # Add more document sources as needed
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
        CREATE TABLE IF NOT EXISTS local_docs (
            doc_id TEXT PRIMARY KEY,
            title TEXT,
            url TEXT,
            published_date TEXT,
            document_type TEXT,
            summary TEXT,
            last_fetched TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Local Documents database initialized")

def fetch_local_documents(url=None):
    """
    Fetch documents from Benton County's website
    
    Args:
        url (str, optional): URL to fetch documents from. If None, uses default URLs.
    
    Returns:
        list: Documents extracted from the webpage
    """
    urls = [url] if url else DEFAULT_DOCUMENT_URLS
    all_docs = []
    
    for url in urls:
        try:
            headers = {
                'User-Agent': 'BentonCountyAssessorPlatform/1.0'
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Error fetching local docs from {url}: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Example: Extract document listings
            # Note: The actual selectors will depend on the website structure
            for item in soup.find_all("div", class_="documentItem"):
                try:
                    title_elem = item.find("a")
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    doc_url = title_elem.get("href", "")
                    
                    # Ensure URL is absolute
                    if doc_url and not doc_url.startswith("http"):
                        if doc_url.startswith("/"):
                            base_url = "/".join(url.split("/")[:3])  # e.g., https://www.example.com
                            doc_url = base_url + doc_url
                        else:
                            doc_url = url.rsplit("/", 1)[0] + "/" + doc_url
                    
                    # Extract ID from URL
                    doc_id = doc_url.split("id=")[-1].split("&")[0] if "id=" in doc_url else f"doc_{len(all_docs)}"
                    
                    # Extract date if available
                    pub_date_elem = item.find("span", class_="pubDate")
                    published_date = pub_date_elem.get_text(strip=True) if pub_date_elem else ""
                    
                    # Extract document type if available
                    doc_type_elem = item.find("span", class_="docType")
                    document_type = doc_type_elem.get_text(strip=True) if doc_type_elem else "Document"
                    
                    # Extract summary if available
                    summary_elem = item.find("div", class_="summary")
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    # Create document record
                    doc = {
                        "doc_id": doc_id,
                        "title": title,
                        "url": doc_url,
                        "published_date": published_date,
                        "document_type": document_type,
                        "summary": summary
                    }
                    
                    all_docs.append(doc)
                    
                except Exception as e:
                    logger.warning(f"Error parsing document item: {str(e)}")
                    continue
            
            logger.info(f"Extracted {len(all_docs)} documents from {url}")
            
        except Exception as e:
            logger.error(f"Error fetching documents from {url}: {str(e)}")
    
    return all_docs

def store_local_document(doc):
    """
    Store or update a local document in the database
    
    Args:
        doc (dict): The document data
    
    Returns:
        bool: Success or failure
    """
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        
        doc_id = doc.get("doc_id", "")
        title = doc.get("title", "")
        url = doc.get("url", "")
        published_date = doc.get("published_date", "")
        document_type = doc.get("document_type", "Document")
        summary = doc.get("summary", "")
        last_fetched = datetime.now().isoformat()
        
        try:
            c.execute('''
                INSERT INTO local_docs 
                (doc_id, title, url, published_date, document_type, summary, last_fetched)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (doc_id, title, url, published_date, document_type, summary, last_fetched))
        except sqlite3.IntegrityError:
            # Document already exists, update it
            c.execute('''
                UPDATE local_docs 
                SET title=?, url=?, published_date=?, document_type=?, summary=?, last_fetched=?
                WHERE doc_id=?
            ''', (title, url, published_date, document_type, summary, last_fetched, doc_id))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error storing local document: {str(e)}")
        return False

def update_all_documents():
    """
    Update all documents from Benton County's website
    
    Returns:
        int: Number of documents updated
    """
    updated_count = 0
    
    try:
        init_db()
        docs = fetch_local_documents()
        
        for doc in docs:
            if store_local_document(doc):
                updated_count += 1
        
        logger.info(f"Updated {updated_count} local documents")
        return updated_count
        
    except Exception as e:
        logger.error(f"Error updating local documents: {str(e)}")
        return 0

def get_local_documents(limit=100):
    """
    Get all tracked local documents
    
    Args:
        limit (int, optional): Maximum number of documents to return
    
    Returns:
        list: A list of document dictionaries
    """
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('''
            SELECT * FROM local_docs
            ORDER BY published_date DESC
            LIMIT ?
        ''', (limit,))
        
        rows = c.fetchall()
        docs = []
        
        for row in rows:
            doc = dict(row)
            doc['bill_id'] = doc['doc_id']  # Ensure consistent bill_id field for compatibility
            doc['title'] = doc['title']
            doc['source'] = 'Benton County'
            docs.append(doc)
        
        conn.close()
        return docs
        
    except Exception as e:
        logger.error(f"Error retrieving local documents: {str(e)}")
        return []

def get_document_by_id(doc_id):
    """
    Get a specific document by its ID
    
    Args:
        doc_id (str): The document ID to retrieve
    
    Returns:
        dict: The document if found, None otherwise
    """
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM local_docs WHERE doc_id = ?', (doc_id,))
        row = c.fetchone()
        
        if row:
            doc = dict(row)
            doc['bill_id'] = doc['doc_id']  # Ensure consistent bill_id field for compatibility
            conn.close()
            return doc
        
        conn.close()
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving local document by ID: {str(e)}")
        return None

def search_documents(query, limit=50):
    """
    Search for documents containing the query in title or summary
    
    Args:
        query (str): The search query
        limit (int, optional): Maximum number of results
    
    Returns:
        list: Matching documents
    """
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        like_query = f'%{query}%'
        c.execute('''
            SELECT * FROM local_docs 
            WHERE title LIKE ? OR summary LIKE ?
            ORDER BY published_date DESC
            LIMIT ?
        ''', (like_query, like_query, limit))
        
        rows = c.fetchall()
        docs = [dict(row) for row in rows]
        
        conn.close()
        return docs
        
    except Exception as e:
        logger.error(f"Error searching local documents: {str(e)}")
        return []

if __name__ == "__main__":
    # Configure logging when run as a standalone script
    logging.basicConfig(level=logging.INFO)
    update_all_documents()