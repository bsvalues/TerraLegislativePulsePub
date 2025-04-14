"""
Bill Analysis Service

This module provides functionality for analyzing legislative bills and their potential
impact on property assessments. It combines bill tracking data with AI analysis.
"""

import logging
from flask import current_app
import re
from services.anthropic_service import get_ai_response
from services.trackers import get_bill_by_id, search_bills

logger = logging.getLogger(__name__)

def analyze_bill_impact(bill_text, bill_title=None, property_class=None, property_value=None, county="Benton"):
    """
    Analyze how a legislative bill impacts property assessments
    
    Args:
        bill_text (str): Full text of the bill
        bill_title (str, optional): Title of the bill
        property_class (str, optional): Property class to focus on
        property_value (float, optional): Property value to consider
        county (str, optional): County focus (default: Benton)
    
    Returns:
        dict: Structured analysis including impact, value change, implications
    """
    try:
        # Construct context for the prompt
        property_context = ""
        if property_class:
            property_context += f"\nFocus specifically on '{property_class}' class properties."
        if property_value:
            property_context += f"\nConsider implications for properties valued around ${property_value:,.2f}."
        
        if not bill_title:
            # Try to extract title from bill text
            title_match = re.search(r"(?i)Title:?\s*(.+?)(?:\n|$)", bill_text[:500])
            bill_title = title_match.group(1).strip() if title_match else "Untitled Bill"
        
        # Construct the prompt for AI analysis
        prompt = f"""
        Analyze how this legislative bill impacts property assessments in {county} County, Washington:
        
        Bill Title: {bill_title}
        
        {property_context}
        
        Bill Text:
        {bill_text}
        
        Provide a detailed, structured analysis that includes:
        1. A summary of the bill's key provisions related to property assessment
        2. Specific impacts on assessment methodology
        3. Potential property value changes (with percentage estimates where possible)
        4. Implementation implications for the assessor's office
        5. Recommendations for handling the changes
        
        Format your response as a detailed analysis followed by specific sections for each of the above points.
        """
        
        # Get the AI response
        response_text = get_ai_response(prompt)
        
        # Extract the potential value change using regex
        value_change_pattern = r"(?i)(increase|decrease).*?(\d+(?:\.\d+)?)%"
        value_change_match = re.search(value_change_pattern, response_text)
        
        value_change = "Unknown"
        if value_change_match:
            direction = value_change_match.group(1).lower()
            percentage = value_change_match.group(2)
            value_change = f"{'+' if direction == 'increase' else '-'}{percentage}%"
        
        # Extract assessment implications
        implications = []
        implications_section = re.search(r"(?i)Implementation implications.*?\n(.*?)(?:\n\d\.|\Z)", 
                                         response_text, re.DOTALL)
        if implications_section:
            implications_text = implications_section.group(1)
            implications = re.findall(r"[-•*]\s*(.*?)(?:\n|$)", implications_text)
            if not implications:
                # If bullet points aren't found, take sentences
                implications = [s.strip() for s in re.split(r'(?<=[.!?])\s+', implications_text) if s.strip()]
                implications = implications[:3]  # Limit to 3 implications
        
        # Extract recommendations
        recommendations = []
        recommendations_section = re.search(r"(?i)Recommendations.*?\n(.*?)(?:\n\d\.|\Z)", 
                                           response_text, re.DOTALL)
        if recommendations_section:
            recommendations_text = recommendations_section.group(1)
            recommendations = re.findall(r"[-•*]\s*(.*?)(?:\n|$)", recommendations_text)
            if not recommendations:
                # If bullet points aren't found, take sentences
                recommendations = [s.strip() for s in re.split(r'(?<=[.!?])\s+', recommendations_text) if s.strip()]
                recommendations = recommendations[:3]  # Limit to 3 recommendations
        
        # Determine confidence level
        confidence_level = "medium"
        if "insufficient data" in response_text.lower() or "unclear" in response_text.lower():
            confidence_level = "low"
        elif "clearly" in response_text.lower() or "significant" in response_text.lower():
            confidence_level = "high"
        
        # Return structured analysis
        return {
            "impact_analysis": response_text,
            "property_value_change": value_change,
            "assessment_implications": implications or ["No specific implications identified"],
            "recommendations": recommendations or ["No specific recommendations provided"],
            "confidence_level": confidence_level,
            "success": True
        }
        
    except Exception as e:
        logger.exception(f"Error analyzing bill impact: {str(e)}")
        return {
            "impact_analysis": f"Error analyzing bill: {str(e)}",
            "property_value_change": "Unknown",
            "assessment_implications": ["Analysis error occurred"],
            "recommendations": ["Contact technical support"],
            "confidence_level": "low",
            "success": False
        }

def analyze_tracked_bill(bill_id, source=None, property_class=None, property_value=None):
    """
    Analyze a bill that is already being tracked
    
    Args:
        bill_id (str): The bill ID
        source (str, optional): The source tracker
        property_class (str, optional): Property class to focus on
        property_value (float, optional): Property value to consider
    
    Returns:
        dict: Structured analysis
    """
    try:
        # Get the bill from trackers
        bill = get_bill_by_id(bill_id, source)
        
        if not bill:
            return {
                "error": f"Bill {bill_id} not found",
                "success": False
            }
        
        # Get the full text if available
        bill_text = bill.get("summary", "")
        if len(bill_text) < 100:  # If summary is too short, try to get more text
            # In a real implementation, we would fetch the full text from the bill URL
            bill_text = f"Bill {bill_id}: {bill.get('title', '')}\n\n{bill.get('description', '')}"
        
        # Analyze the bill
        analysis = analyze_bill_impact(
            bill_text=bill_text,
            bill_title=bill.get("title", f"Bill {bill_id}"),
            property_class=property_class,
            property_value=property_value
        )
        
        # Add bill metadata to the analysis
        analysis["bill_id"] = bill_id
        analysis["bill_title"] = bill.get("title", "")
        analysis["bill_source"] = bill.get("source", source or "unknown")
        analysis["bill_url"] = bill.get("url", bill.get("link", ""))
        analysis["bill_status"] = bill.get("status", "unknown")
        
        return analysis
        
    except Exception as e:
        logger.exception(f"Error analyzing tracked bill: {str(e)}")
        return {
            "error": f"Error analyzing bill: {str(e)}",
            "success": False
        }

def summarize_bill(bill_text, bill_title=None, summary_type="general", length="medium"):
    """
    Generate a summary of a bill
    
    Args:
        bill_text (str): Full text of the bill
        bill_title (str, optional): Title of the bill
        summary_type (str, optional): Type of summary (general, technical, public)
        length (str, optional): Length of summary (short, medium, long)
    
    Returns:
        dict: The bill summary
    """
    try:
        if not bill_title:
            # Try to extract title from bill text
            title_match = re.search(r"(?i)Title:?\s*(.+?)(?:\n|$)", bill_text[:500])
            bill_title = title_match.group(1).strip() if title_match else "Untitled Bill"
        
        # Define word count targets based on length
        word_counts = {
            'short': 150,
            'medium': 300,
            'long': 500
        }
        
        # Define audience for different summary types
        audience_guidance = {
            'general': "for assessor staff with some knowledge of property assessment",
            'technical': "for technical staff with expertise in property assessment and taxation",
            'public': "for the general public with limited knowledge of property assessment processes"
        }
        
        target_words = word_counts.get(length, 300)
        audience = audience_guidance.get(summary_type, audience_guidance['general'])
        
        # Construct the prompt
        prompt = f"""
        Summarize this legislative bill:
        
        Title: {bill_title}
        
        Please provide a {length} summary (about {target_words} words) {audience}.
        Focus on provisions related to property assessment, taxation, or valuation.
        
        Bill Text:
        {bill_text}
        """
        
        # Get the AI response
        summary_text = get_ai_response(prompt, max_tokens=target_words * 2)
        
        # Calculate actual word count
        word_count = len(summary_text.split())
        
        # Return structured response
        return {
            "summary": summary_text,
            "summary_type": summary_type,
            "length": length,
            "target_word_count": target_words,
            "actual_word_count": word_count,
            "success": True
        }
        
    except Exception as e:
        logger.exception(f"Error summarizing bill: {str(e)}")
        return {
            "error": f"Error summarizing bill: {str(e)}",
            "success": False
        }

def extract_entities(bill_text, bill_title=None, entity_types=None):
    """
    Extract entities from a bill
    
    Args:
        bill_text (str): Full text of the bill
        bill_title (str, optional): Title of the bill
        entity_types (list, optional): Types of entities to extract
    
    Returns:
        dict: Extracted entities
    """
    try:
        if not entity_types:
            entity_types = ["organization", "person", "location", "date", "money", "percentage"]
            
        if not bill_title:
            # Try to extract title from bill text
            title_match = re.search(r"(?i)Title:?\s*(.+?)(?:\n|$)", bill_text[:500])
            bill_title = title_match.group(1).strip() if title_match else "Untitled Bill"
        
        # Construct the prompt
        prompt = f"""
        Extract the following types of entities from this legislative bill:
        {', '.join(entity_types)}
        
        Title: {bill_title}
        
        Bill Text:
        {bill_text}
        
        For each entity found, provide:
        1. The exact text of the entity
        2. The entity type
        3. The context (sentence or clause where it appears)
        
        Format your response as a JSON object with each entity type as a key and a list of objects containing
        the entity text, type, and context. Use this format exactly:
        
        ```json
        {{
          "organizations": [
            {{ "text": "Department of Revenue", "context": "The Department of Revenue shall..." }}
          ],
          "persons": [
            {{ "text": "John Smith", "context": "Representative John Smith introduced..." }}
          ]
        }}
        ```
        """
        
        # Get the AI response
        response_text = get_ai_response(prompt)
        
        # Extract JSON from response (basic approach)
        json_pattern = r"```json\s*(.*?)\s*```"
        json_match = re.search(json_pattern, response_text, re.DOTALL)
        
        entities_text = response_text
        if json_match:
            entities_text = json_match.group(1)
        
        # Return structured response
        return {
            "extracted_entities": entities_text,
            "entity_types": entity_types,
            "success": True
        }
        
    except Exception as e:
        logger.exception(f"Error extracting entities: {str(e)}")
        return {
            "error": f"Error extracting entities: {str(e)}",
            "success": False
        }

def search_relevant_bills(query, limit=10):
    """
    Search for bills relevant to a query across all trackers
    
    Args:
        query (str): The search query
        limit (int, optional): Maximum number of results per source
    
    Returns:
        dict: Bills grouped by source
    """
    try:
        results = search_bills(query)
        
        # Group by source
        grouped_results = {}
        for bill in results:
            source = bill.get("source", "unknown")
            if source not in grouped_results:
                grouped_results[source] = []
            
            if len(grouped_results[source]) < limit:
                grouped_results[source].append(bill)
        
        return {
            "query": query,
            "results_by_source": grouped_results,
            "total_results": sum(len(bills) for bills in grouped_results.values()),
            "success": True
        }
        
    except Exception as e:
        logger.exception(f"Error searching bills: {str(e)}")
        return {
            "error": f"Error searching bills: {str(e)}",
            "success": False
        }