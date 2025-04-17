"""
Bill Analysis Service

This service provides functions for analyzing legislative bills using the Anthropic API.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional
from flask import current_app

from models import LegislativeUpdate, db
from services.anthropic_service import generate_bill_summary, extract_bill_entities, analyze_bill_impact
from services.bill_search_service import get_bill_by_id

logger = logging.getLogger(__name__)

def analyze_tracked_bill(bill_id: str, analysis_type: str, source: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a tracked bill using AI
    
    Args:
        bill_id (str): The bill ID
        analysis_type (str): Type of analysis - 'summary', 'entities', or 'impact'
        source (str, optional): Source of the bill
        
    Returns:
        dict: Analysis results
    """
    # Get the bill
    bill = get_bill_by_id(bill_id, source)
    
    if not bill:
        logger.error(f"Bill {bill_id} not found for analysis")
        return {"error": f"Bill {bill_id} not found"}
    
    # Check if we have bill text
    if not bill.get('description'):
        logger.error(f"Bill {bill_id} has no text to analyze")
        return {"error": f"Bill {bill_id} has no text to analyze"}
    
    bill_text = bill.get('description')
    bill_title = bill.get('title')
    
    # Perform the requested analysis
    try:
        if analysis_type == 'summary':
            result = generate_bill_summary(bill_text, bill_title)
        elif analysis_type == 'entities':
            result = extract_bill_entities(bill_text, bill_title)
        elif analysis_type == 'impact':
            result = analyze_bill_impact(bill_text, bill_title)
        else:
            return {"error": f"Unknown analysis type: {analysis_type}"}
        
        # Update the bill in the database with the analysis results
        update_bill_with_analysis(bill.get('id'), analysis_type, result)
        
        return result
    except Exception as e:
        logger.exception(f"Error analyzing bill {bill_id}: {str(e)}")
        return {"error": f"Analysis failed: {str(e)}"}

def categorize_bill(bill_id: str, source: Optional[str] = None) -> Dict[str, Any]:
    """
    Categorize a bill based on affected property classes and impact level
    
    Args:
        bill_id (str): The bill ID
        source (str, optional): Source of the bill
        
    Returns:
        dict: Categorization results
    """
    # Get the bill
    bill = get_bill_by_id(bill_id, source)
    
    if not bill:
        logger.error(f"Bill {bill_id} not found for categorization")
        return {"error": f"Bill {bill_id} not found"}
    
    # Analyze the bill impact
    impact_analysis = analyze_tracked_bill(bill_id, 'impact', source)
    
    if "error" in impact_analysis:
        return impact_analysis
    
    # Extract property classes and impact level
    property_classes = impact_analysis.get('affected_property_classes', [])
    impact_level = impact_analysis.get('impact_level', 'Unknown')
    
    # Update the bill in the database
    update_bill_classification(
        bill.get('id'),
        property_classes, 
        impact_level
    )
    
    return {
        "bill_id": bill_id,
        "affected_property_classes": property_classes,
        "impact_level": impact_level
    }

def batch_analyze_bills(bill_ids: List[str], analysis_type: str) -> Dict[str, Any]:
    """
    Analyze multiple bills in batch
    
    Args:
        bill_ids (list): List of bill IDs
        analysis_type (str): Type of analysis - 'summary', 'entities', or 'impact'
        
    Returns:
        dict: Batch analysis results
    """
    results = {}
    errors = []
    
    for bill_id in bill_ids:
        logger.info(f"Analyzing bill {bill_id}")
        result = analyze_tracked_bill(bill_id, analysis_type)
        
        if "error" in result:
            errors.append({"bill_id": bill_id, "error": result["error"]})
        else:
            results[bill_id] = result
    
    return {
        "results": results,
        "errors": errors,
        "total": len(bill_ids),
        "successful": len(results),
        "failed": len(errors)
    }

def update_bill_with_analysis(bill_id: int, analysis_type: str, analysis_result: Dict[str, Any]) -> None:
    """
    Update a bill with analysis results
    
    Args:
        bill_id (int): The bill database ID
        analysis_type (str): Type of analysis
        analysis_result (dict): Analysis results
    """
    try:
        bill = LegislativeUpdate.query.get(bill_id)
        
        if not bill:
            logger.error(f"Bill with ID {bill_id} not found in database")
            return
        
        if analysis_type == 'impact':
            # Extract impact summary
            impact_summary = analysis_result.get('summary', '')
            bill.impact_summary = impact_summary
        
        db.session.commit()
        logger.info(f"Updated bill {bill.bill_id} with {analysis_type} analysis")
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error updating bill with analysis: {str(e)}")

def update_bill_classification(bill_id: int, property_classes: List[str], impact_level: str) -> None:
    """
    Update a bill with property class and impact classification
    
    Args:
        bill_id (int): The bill database ID
        property_classes (list): List of affected property classes
        impact_level (str): Impact level (High, Medium, Low)
    """
    try:
        bill = LegislativeUpdate.query.get(bill_id)
        
        if not bill:
            logger.error(f"Bill with ID {bill_id} not found in database")
            return
        
        # Join property classes with comma
        bill.affected_property_classes = ", ".join(property_classes)
        
        db.session.commit()
        logger.info(f"Updated bill {bill.bill_id} with property class classification")
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error updating bill classification: {str(e)}")