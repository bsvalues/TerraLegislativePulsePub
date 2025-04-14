"""
Bill Search Service

This service provides functions for searching and retrieving legislative bills
from the database.
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, desc
from flask import current_app

from models import LegislativeUpdate, db

logger = logging.getLogger(__name__)

def get_all_tracked_bills(limit=100, offset=0, source=None):
    """
    Get all tracked bills with optional source filtering
    
    Args:
        limit (int): Maximum number of bills to return
        offset (int): Offset for pagination
        source (str): Optional source filter
        
    Returns:
        list: List of bills
    """
    query = LegislativeUpdate.query
    
    if source:
        query = query.filter(LegislativeUpdate.source == source)
    
    bills = query.order_by(desc(LegislativeUpdate.last_action_date)) \
                .limit(limit) \
                .offset(offset) \
                .all()
    
    return [bill_to_dict(bill) for bill in bills]

def search_bills(search_term, sources=None, limit=100, offset=0):
    """
    Search for bills by title, description, or bill ID
    
    Args:
        search_term (str): Search term
        sources (list): List of sources to search
        limit (int): Maximum number of bills to return
        offset (int): Offset for pagination
        
    Returns:
        list: List of bills matching the search criteria
    """
    search_pattern = f"%{search_term}%"
    
    query = LegislativeUpdate.query.filter(
        or_(
            LegislativeUpdate.title.ilike(search_pattern),
            LegislativeUpdate.description.ilike(search_pattern),
            LegislativeUpdate.bill_id.ilike(search_pattern)
        )
    )
    
    if sources:
        query = query.filter(LegislativeUpdate.source.in_(sources))
    
    bills = query.order_by(desc(LegislativeUpdate.last_action_date)) \
                .limit(limit) \
                .offset(offset) \
                .all()
    
    return [bill_to_dict(bill) for bill in bills]

def get_bill_by_id(bill_id, source=None):
    """
    Get a specific bill by ID
    
    Args:
        bill_id (str): The bill ID
        source (str): Optional source filter
        
    Returns:
        dict: Bill data or None if not found
    """
    query = LegislativeUpdate.query.filter(LegislativeUpdate.bill_id == bill_id)
    
    if source:
        query = query.filter(LegislativeUpdate.source == source)
    
    bill = query.first()
    
    if bill:
        return bill_to_dict(bill)
    
    return None

def search_relevant_bills(property_class, keywords=None, limit=50):
    """
    Search for bills relevant to a specific property class
    
    Args:
        property_class (str): The property class (e.g., 'Residential')
        keywords (list): Optional list of keywords to further filter results
        limit (int): Maximum number of bills to return
        
    Returns:
        list: List of bills relevant to the property class
    """
    property_class_pattern = f"%{property_class}%"
    
    # Start with bills that explicitly mention the property class
    query = LegislativeUpdate.query.filter(
        or_(
            LegislativeUpdate.affected_property_classes.ilike(property_class_pattern),
            LegislativeUpdate.title.ilike(property_class_pattern),
            LegislativeUpdate.description.ilike(property_class_pattern)
        )
    )
    
    # Apply keyword filters if provided
    if keywords and len(keywords) > 0:
        keyword_filters = []
        for keyword in keywords:
            keyword_pattern = f"%{keyword}%"
            keyword_filters.append(
                or_(
                    LegislativeUpdate.title.ilike(keyword_pattern),
                    LegislativeUpdate.description.ilike(keyword_pattern)
                )
            )
        query = query.filter(or_(*keyword_filters))
    
    bills = query.order_by(desc(LegislativeUpdate.last_action_date)) \
                .limit(limit) \
                .all()
    
    return [bill_to_dict(bill) for bill in bills]

def get_recent_bills(days=30, limit=10):
    """
    Get bills updated in the last N days
    
    Args:
        days (int): Number of days to look back
        limit (int): Maximum number of bills to return
        
    Returns:
        list: List of recent bills
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    bills = LegislativeUpdate.query \
        .filter(LegislativeUpdate.last_action_date >= cutoff_date) \
        .order_by(desc(LegislativeUpdate.last_action_date)) \
        .limit(limit) \
        .all()
    
    return [bill_to_dict(bill) for bill in bills]

def get_high_impact_bills(limit=10):
    """
    Get bills with high impact (based on analysis)
    
    Args:
        limit (int): Maximum number of bills to return
        
    Returns:
        list: List of high-impact bills
    """
    # This is a simplified implementation. In a production system,
    # we would have a more sophisticated impact scoring mechanism.
    bills = LegislativeUpdate.query \
        .filter(LegislativeUpdate.impact_summary.isnot(None)) \
        .order_by(desc(LegislativeUpdate.last_action_date)) \
        .limit(limit) \
        .all()
    
    return [bill_to_dict(bill) for bill in bills]

def bill_to_dict(bill):
    """
    Convert a LegislativeUpdate model to a dictionary
    
    Args:
        bill (LegislativeUpdate): The bill model
        
    Returns:
        dict: Dictionary representation of the bill
    """
    return {
        'id': bill.id,
        'bill_id': bill.bill_id,
        'title': bill.title,
        'description': bill.description,
        'source': bill.source,
        'url': bill.url,
        'status': bill.status,
        'introduced_date': bill.introduced_date.strftime('%Y-%m-%d') if bill.introduced_date else None,
        'last_action_date': bill.last_action_date.strftime('%Y-%m-%d') if bill.last_action_date else None,
        'impact_summary': bill.impact_summary,
        'affected_property_classes': bill.affected_property_classes,
        'created_at': bill.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': bill.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    }