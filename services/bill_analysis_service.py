"""
Bill Analysis Service

This module provides functionality for analyzing legislative bills.
"""

import logging
from typing import Optional, Dict, Any

from flask import current_app
from services.anthropic_service import get_ai_response, generate_bill_summary, extract_entities, analyze_bill_impact, summarize_bill
from models import LegislativeUpdate, db

logger = logging.getLogger(__name__)

def analyze_tracked_bill(bill_id: str, analysis_type: str = 'impact', property_class: Optional[str] = None, source: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a tracked bill in the database
    
    Args:
        bill_id (str): The ID of the bill to analyze
        analysis_type (str): The type of analysis to perform (impact, summary, entities)
        property_class (str, optional): Specific property class to analyze impact for
        source (str, optional): The source of the bill
        
    Returns:
        Dict[str, Any]: The analysis results
    """
    try:
        # Build the query
        query = LegislativeUpdate.query.filter_by(bill_id=bill_id)
        
        # Add source filter if provided
        if source:
            query = query.filter_by(source=source)
            
        # Find the bill in the database
        bill = query.first()
        
        if not bill:
            return {
                "success": False,
                "error": f"Bill {bill_id} not found in the database"
            }
        
        # Get the bill text from the appropriate source
        bill_text = get_bill_text(bill)
        
        if not bill_text:
            return {
                "success": False,
                "error": f"Could not retrieve text for bill {bill_id}"
            }
        
        # Perform the requested analysis
        if analysis_type == 'impact':
            result = analyze_bill_impact(bill_text, bill.title, property_class)
            
            # Store the impact summary if the analysis was successful
            if result['success'] and 'analysis' in result:
                bill.impact_summary = result['analysis'][:1000]  # Store a truncated version
                db.session.commit()
                
            return result
            
        elif analysis_type == 'summary':
            return generate_bill_summary(bill_text, bill.title)
            
        elif analysis_type == 'entities':
            return extract_entities(bill_text, bill.title)
            
        else:
            return {
                "success": False,
                "error": f"Unknown analysis type: {analysis_type}"
            }
    
    except Exception as e:
        logger.exception(f"Error analyzing bill {bill_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_bill_text(bill: LegislativeUpdate) -> Optional[str]:
    """
    Get the text of a bill from the appropriate source
    
    Args:
        bill (LegislativeUpdate): The bill to get text for
        
    Returns:
        Optional[str]: The bill text, or None if it could not be retrieved
    """
    try:
        # Use the source to determine how to get the bill text
        source = bill.source.lower()
        
        if source == 'wa_legislature':
            # Get text from WA Legislature website
            from services.trackers.wa_legislature import get_bill_text_by_id
            return get_bill_text_by_id(bill.bill_id)
            
        elif source == 'openstates':
            # Get text from OpenStates API
            from services.trackers.openstates import get_bill_text_by_id
            return get_bill_text_by_id(bill.bill_id)
            
        elif source == 'legiscan':
            # Get text from LegiScan API
            from services.trackers.legiscan import get_bill_text_by_id
            return get_bill_text_by_id(bill.bill_id)
            
        elif source == 'local_docs':
            # Get text from local document repository
            from services.trackers.local_docs import get_document_text_by_id
            return get_document_text_by_id(bill.bill_id)
            
        else:
            logger.warning(f"Unknown bill source: {source}")
            return None
    
    except Exception as e:
        logger.exception(f"Error getting text for bill {bill.bill_id}: {str(e)}")
        return None

def categorize_bill(bill_text: str, bill_title: Optional[str] = None) -> Dict[str, Any]:
    """
    Categorize a bill by topic and relevance to property assessment
    
    Args:
        bill_text (str): The text of the bill
        bill_title (str, optional): The title of the bill
        
    Returns:
        Dict[str, Any]: The categorization results
    """
    try:
        # Build the prompt
        title_text = f"Title: {bill_title}\n\n" if bill_title else ""
        
        prompt = f"""
        Categorize this bill related to property assessment and taxation:
        
        {title_text}
        Bill Text:
        ```
        {bill_text[:10000]}
        ```
        
        Provide the following information in JSON format:
        
        1. Primary category (one of: "Property Tax", "Assessment Methodology", "Exemptions", "Appeals Process", "Administrative", "Unrelated")
        
        2. Relevance to county assessor operations (score from 0-10, where 10 is highly relevant)
        
        3. Affected property types (list all that apply from: "Residential", "Commercial", "Industrial", "Agricultural", "Vacant Land", "Public")
        
        4. Impact level (one of: "High", "Medium", "Low", "Unknown")
        
        5. Top 3 keywords that describe this bill
        
        Format your response as a JSON object with keys: "category", "relevance_score", "affected_property_types", "impact_level", and "keywords".
        """
        
        # Get categorization from Claude
        system_prompt = "You are a legislative analyst for a county assessor's office. You specialize in categorizing bills related to property assessment and taxation."
        
        response = get_ai_response(prompt, system_prompt, temperature=0.1)
        
        # Parse the JSON response
        import json
        import re
        
        # Extract JSON object from response (it might be in a code block)
        json_match = re.search(r'```(?:json)?(.*?)```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            # If no code block, try to use the whole response
            json_str = response.strip()
        
        # Parse JSON
        try:
            categories = json.loads(json_str)
            return {
                "success": True,
                "categories": categories,
                "bill_title": bill_title
            }
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing categorization JSON: {str(e)}")
            return {
                "success": False,
                "error": f"Error parsing categorization: {str(e)}",
                "raw_response": response
            }
    
    except Exception as e:
        logger.exception(f"Error categorizing bill: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }