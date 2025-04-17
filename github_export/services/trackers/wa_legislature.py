"""
Washington State Legislature Tracker

This module provides functionality for tracking bills from the Washington State Legislature.
It fetches bill data from the Washington State Legislature website and RSS feeds.
"""

import logging
import re
import ssl
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urljoin

import feedparser
import requests
from bs4 import BeautifulSoup
from flask import current_app
import json

from models import LegislativeUpdate, db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, and_

logger = logging.getLogger(__name__)

# Constants
WA_LEG_BASE_URL = "https://app.leg.wa.gov"
WA_LEG_RSS_URL = "https://app.leg.wa.gov/billsbytopic/default.aspx"
WA_LEG_BILL_API_URL = "https://app.leg.wa.gov/api/search"
WA_LEG_SEARCH_URL = "https://app.leg.wa.gov/billsummary"

# Property assessment related topics and keywords
PROPERTY_ASSESSMENT_TOPICS = [
    "Taxes - Property",
    "Land Use & Planning",
    "Housing",
    "Growth Management",
    "Environment",
    "Special Districts"
]

PROPERTY_KEYWORDS = [
    "property tax", "assessment", "valuation", "appraisal", "levy", "real estate", 
    "residential property", "commercial property", "agricultural land", "exemption"
]

def init_db():
    """Initialize the database for the WA Legislature tracker"""
    logger.info("WA Legislature database initialized")

def fetch_and_store() -> int:
    """
    Fetch bills from the WA Legislature API and store them in the database
    
    Returns:
        int: The number of bills added or updated
    """
    try:
        logger.info("Fetching bills from WA Legislature")
        updated_count = 0
        
        # Get bills by property-related keywords
        for keyword in PROPERTY_KEYWORDS:
            bills = search_bills_by_keyword(keyword)
            for bill in bills:
                if save_bill(bill):
                    updated_count += 1
        
        # Get bills by relevant topics
        for topic in PROPERTY_ASSESSMENT_TOPICS:
            bills = get_bills_by_topic(topic)
            for bill in bills:
                if save_bill(bill):
                    updated_count += 1
        
        logger.info(f"Updated {updated_count} bills from WA Legislature")
        return updated_count
    
    except Exception as e:
        logger.exception(f"Error fetching from WA Legislature: {str(e)}")
        return 0

def search_bills_by_keyword(keyword: str) -> List[Dict[str, Any]]:
    """
    Search for bills by keyword using the WA Legislature API
    
    Args:
        keyword (str): The keyword to search for
        
    Returns:
        List[Dict[str, Any]]: List of bills matching the keyword
    """
    try:
        logger.info(f"Searching WA Legislature for bills with keyword: {keyword}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json'
        }
        
        # Create search parameters
        current_year = datetime.now().year
        biennium = f"{current_year - 1}-{current_year}"
        
        params = {
            'Term': keyword,
            'Biennium': biennium,
            'SearchCriteria.PageSize': 50,
            'SearchCriteria.DocumentType': 'Bills'
        }
        
        # Make the API request with SSL context
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        response = requests.get(
            WA_LEG_BILL_API_URL,
            params=params,
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"Error searching WA Legislature: {response.status_code}")
            return []
        
        # Parse JSON response
        data = response.json()
        results = []
        
        if 'ResultList' in data and data['ResultList']:
            for result in data['ResultList']:
                bill_id = result.get('DocumentNumber')
                if bill_id:
                    # Get bill details
                    bill_details = get_bill_details(bill_id)
                    if bill_details:
                        results.append(bill_details)
        
        logger.info(f"Found {len(results)} bills matching keyword '{keyword}'")
        return results
    
    except Exception as e:
        logger.exception(f"Error searching WA Legislature for '{keyword}': {str(e)}")
        return []

def get_bills_by_topic(topic: str) -> List[Dict[str, Any]]:
    """
    Get bills for a specific topic from the WA Legislature website
    
    Args:
        topic (str): The topic to get bills for
        
    Returns:
        List[Dict[str, Any]]: List of bills related to the topic
    """
    try:
        logger.info(f"Getting WA Legislature bills for topic: {topic}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Get the topic page
        topic_url = f"{WA_LEG_RSS_URL}?topic={topic.replace(' ', '%20')}"
        response = requests.get(topic_url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Error getting topic page: {response.status_code}")
            return []
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        bill_links = soup.select('.billsbytopiclink a')
        
        results = []
        for link in bill_links:
            bill_id = link.text.strip()
            if bill_id:
                # Get bill details
                bill_details = get_bill_details(bill_id)
                if bill_details:
                    results.append(bill_details)
        
        logger.info(f"Found {len(results)} bills for topic '{topic}'")
        return results
    
    except Exception as e:
        logger.exception(f"Error getting bills for topic '{topic}': {str(e)}")
        return []

def get_bill_details(bill_id: str) -> Optional[Dict[str, Any]]:
    """
    Get details for a specific bill
    
    Args:
        bill_id (str): The ID of the bill (e.g. 'HB 1234')
        
    Returns:
        Optional[Dict[str, Any]]: Bill details or None if not found
    """
    try:
        logger.info(f"Getting details for bill {bill_id}")
        
        # Remove any spaces in the bill ID
        bill_num = bill_id.replace(' ', '')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Get the bill summary page
        current_year = datetime.now().year
        url = f"{WA_LEG_SEARCH_URL}?BillNumber={bill_num}&Year={current_year}"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Error getting bill details: {response.status_code}")
            return None
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract bill title
        title_elem = soup.select_one('h1.billsummary')
        title = title_elem.text.strip() if title_elem else f"Washington State Bill {bill_id}"
        
        # Extract bill description/text
        description = get_bill_text_by_id(bill_id)
        if not description:
            description = "Bill text not available."
        
        # Extract status
        status_elem = soup.select_one('.billstatusdescription')
        status = status_elem.text.strip() if status_elem else "Pending"
        
        # Extract dates
        introduced_date = None
        last_action_date = None
        date_elems = soup.select('.actionitems')
        if date_elems:
            # First date is usually introduction date
            first_date = date_elems[0].select_one('.dateaction')
            if first_date:
                try:
                    introduced_date = datetime.strptime(first_date.text.strip(), '%m/%d/%Y')
                except ValueError:
                    introduced_date = datetime.now()
            
            # Last date is the most recent action
            last_date = date_elems[-1].select_one('.dateaction')
            if last_date:
                try:
                    last_action_date = datetime.strptime(last_date.text.strip(), '%m/%d/%Y')
                except ValueError:
                    last_action_date = datetime.now()
        
        # Create the bill data dictionary
        bill_data = {
            'bill_id': bill_id,
            'title': title,
            'description': description,
            'source': 'wa_legislature',
            'url': url,
            'status': get_status_from_text(status),
            'introduced_date': introduced_date or datetime.now(),
            'last_action_date': last_action_date or datetime.now(),
            'impact_summary': None,  # This will be filled in by AI analysis
            'affected_property_classes': None  # This will be filled in by AI analysis
        }
        
        return bill_data
    
    except Exception as e:
        logger.exception(f"Error getting details for bill {bill_id}: {str(e)}")
        return None

def get_bill_text_by_id(bill_id: str) -> Optional[str]:
    """
    Get the text of a bill from the WA Legislature website
    
    Args:
        bill_id (str): The ID of the bill
        
    Returns:
        Optional[str]: The bill text, or None if it could not be retrieved
    """
    try:
        logger.info(f"Getting bill text for {bill_id} from WA Legislature")
        
        # Remove any spaces in the bill ID
        bill_num = bill_id.replace(' ', '')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Get the bill documents page
        current_year = datetime.now().year
        url = f"{WA_LEG_BASE_URL}/billsummary?BillNumber={bill_num}&Year={current_year}"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Error getting bill page: {response.status_code}")
            return None
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for links to bill text in the document section
        doc_links = soup.select('#documentGrid a')
        
        for link in doc_links:
            if 'Original Bill' in link.text or 'Substitute Bill' in link.text:
                doc_url = link.get('href')
                if doc_url:
                    # Make the full URL
                    full_url = urljoin(WA_LEG_BASE_URL, doc_url)
                    
                    # Get the document
                    doc_response = requests.get(full_url, headers=headers)
                    
                    if doc_response.status_code == 200:
                        # Parse the document
                        doc_soup = BeautifulSoup(doc_response.text, 'html.parser')
                        
                        # Extract the bill text
                        text_sections = doc_soup.select('.billsection')
                        
                        # If we found text sections, join them
                        if text_sections:
                            bill_text = '\n\n'.join([section.text.strip() for section in text_sections])
                            return bill_text
        
        # If we couldn't find the text, get the digest
        digest_elem = soup.select_one('#digest')
        if digest_elem:
            return digest_elem.text.strip()
        
        # If nothing else works, extract whatever text we can from the page
        bill_text = soup.get_text().strip()
        return bill_text[:10000]  # Limit to 10000 chars in case the page is huge
    
    except Exception as e:
        logger.exception(f"Error getting text for bill {bill_id}: {str(e)}")
        return None

def save_bill(bill_data: Dict[str, Any]) -> bool:
    """
    Save a bill to the database, updating if it already exists
    
    Args:
        bill_data (Dict[str, Any]): The bill data to save
        
    Returns:
        bool: True if the bill was added or updated, False otherwise
    """
    try:
        # Check if the bill already exists
        bill = LegislativeUpdate.query.filter_by(
            bill_id=bill_data['bill_id'],
            source=bill_data['source']
        ).first()
        
        if bill:
            # Update existing bill
            bill.title = bill_data['title']
            bill.description = bill_data['description']
            bill.url = bill_data['url']
            bill.status = bill_data['status']
            
            if 'introduced_date' in bill_data and bill_data['introduced_date']:
                bill.introduced_date = bill_data['introduced_date']
                
            if 'last_action_date' in bill_data and bill_data['last_action_date']:
                bill.last_action_date = bill_data['last_action_date']
            
            bill.updated_at = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"Updated bill {bill_data['bill_id']} from {bill_data['source']}")
            return True
        else:
            # Add new bill
            new_bill = LegislativeUpdate(
                bill_id=bill_data['bill_id'],
                title=bill_data['title'],
                description=bill_data['description'],
                source=bill_data['source'],
                url=bill_data['url'],
                status=bill_data['status'],
                introduced_date=bill_data.get('introduced_date', datetime.utcnow()),
                last_action_date=bill_data.get('last_action_date', datetime.utcnow()),
                impact_summary=bill_data.get('impact_summary'),
                affected_property_classes=bill_data.get('affected_property_classes'),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(new_bill)
            db.session.commit()
            logger.info(f"Added new bill {bill_data['bill_id']} from {bill_data['source']}")
            return True
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.exception(f"Database error saving bill {bill_data['bill_id']}: {str(e)}")
        return False
    except Exception as e:
        logger.exception(f"Error saving bill {bill_data['bill_id']}: {str(e)}")
        return False

def get_status_from_text(status_text: str) -> str:
    """
    Convert a status text from the website to a standardized status
    
    Args:
        status_text (str): The status text from the website
        
    Returns:
        str: A standardized status (Active, Passed, Failed, Pending)
    """
    status_text = status_text.lower()
    
    if any(term in status_text for term in ['signed', 'enacted', 'passed both', 'chaptered']):
        return 'Passed'
    elif any(term in status_text for term in ['died', 'failed', 'vetoed']):
        return 'Failed'
    elif any(term in status_text for term in ['in committee', 'first reading', 'introduced', 'prefiled']):
        return 'Pending'
    else:
        return 'Active'