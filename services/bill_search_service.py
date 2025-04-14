"""
Bill Search Service

This module provides functionality for searching and retrieving bills.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

from flask import current_app
from models import LegislativeUpdate

logger = logging.getLogger(__name__)

def get_all_tracked_bills(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get all tracked bills
    
    Args:
        limit (int): Maximum number of bills to retrieve
        offset (int): Offset for pagination
        
    Returns:
        List[Dict[str, Any]]: List of bills
    """
    try:
        # Query the database for all tracked bills
        bills = LegislativeUpdate.query.order_by(
            LegislativeUpdate.last_action_date.desc()
        ).limit(limit).offset(offset).all()
        
        # Convert to dictionary format
        return [_bill_to_dict(bill) for bill in bills]
        
    except Exception as e:
        logger.exception(f"Error getting all tracked bills: {str(e)}")
        return []

def search_bills(query: str, sources: Optional[List[str]] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search for bills by keyword
    
    Args:
        query (str): Search query
        sources (List[str], optional): List of sources to search (e.g., ['wa_legislature', 'openstates'])
        limit (int): Maximum number of results to return
        
    Returns:
        List[Dict[str, Any]]: Search results
    """
    try:
        # Start with a base query
        base_query = LegislativeUpdate.query
        
        # Add source filter if provided
        if sources:
            base_query = base_query.filter(LegislativeUpdate.source.in_(sources))
        
        # Add search conditions (searching in title and description)
        search_query = base_query.filter(
            (LegislativeUpdate.title.ilike(f'%{query}%')) | 
            (LegislativeUpdate.description.ilike(f'%{query}%'))
        ).order_by(LegislativeUpdate.last_action_date.desc()).limit(limit)
        
        # Execute the query
        bills = search_query.all()
        
        # Convert to dictionary format
        return [_bill_to_dict(bill) for bill in bills]
        
    except Exception as e:
        logger.exception(f"Error searching bills: {str(e)}")
        return []

def get_bill_by_id(bill_id: str, source: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get a specific bill by ID
    
    Args:
        bill_id (str): The bill ID
        source (str, optional): The source of the bill
        
    Returns:
        Optional[Dict[str, Any]]: The bill data, or None if not found
    """
    try:
        # Build the query
        query = LegislativeUpdate.query.filter_by(bill_id=bill_id)
        
        # Add source filter if provided
        if source:
            query = query.filter_by(source=source)
            
        # Find the bill
        bill = query.first()
        
        # Return as dictionary if found
        return _bill_to_dict(bill) if bill else None
        
    except Exception as e:
        logger.exception(f"Error getting bill {bill_id}: {str(e)}")
        return None

def search_relevant_bills(property_class: str, keywords: Optional[List[str]] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for bills relevant to a particular property class and/or keywords
    
    Args:
        property_class (str): The property class (e.g., 'Residential', 'Commercial')
        keywords (List[str], optional): Additional keywords to consider
        limit (int): Maximum number of results to return
        
    Returns:
        List[Dict[str, Any]]: Relevant bills
    """
    try:
        # Start with a base query that looks for the property class
        base_query = LegislativeUpdate.query.filter(
            LegislativeUpdate.affected_property_classes.ilike(f'%{property_class}%')
        )
        
        # Add keyword filters if provided
        if keywords and len(keywords) > 0:
            for keyword in keywords:
                base_query = base_query.filter(
                    (LegislativeUpdate.title.ilike(f'%{keyword}%')) | 
                    (LegislativeUpdate.description.ilike(f'%{keyword}%'))
                )
        
        # Order by last action date and impact summary presence
        # (bills with impact summaries are more likely to be relevant)
        bills = base_query.order_by(
            LegislativeUpdate.impact_summary.is_(None),  # Bills with impact summaries first
            LegislativeUpdate.last_action_date.desc()    # Then by date
        ).limit(limit).all()
        
        # Convert to dictionary format
        return [_bill_to_dict(bill) for bill in bills]
        
    except Exception as e:
        logger.exception(f"Error finding relevant bills for {property_class}: {str(e)}")
        return []

def _bill_to_dict(bill: LegislativeUpdate) -> Dict[str, Any]:
    """
    Convert a LegislativeUpdate model to a dictionary
    
    Args:
        bill (LegislativeUpdate): The bill to convert
        
    Returns:
        Dict[str, Any]: Dictionary representation of the bill
    """
    return {
        'id': bill.id,
        'bill_id': bill.bill_id,
        'title': bill.title,
        'description': bill.description,
        'source': bill.source,
        'url': bill.url,
        'status': bill.status,
        'introduced_date': bill.introduced_date.isoformat() if bill.introduced_date else None,
        'last_action_date': bill.last_action_date.isoformat() if bill.last_action_date else None,
        'impact_summary': bill.impact_summary,
        'affected_property_classes': bill.affected_property_classes,
        'created_at': bill.created_at.isoformat(),
        'updated_at': bill.updated_at.isoformat()
    }