"""
Anthropic Service

This service provides functions for interacting with the Anthropic API to analyze
legislative bills.
"""

import logging
import json
import os
import sys
from typing import Dict, Any, List, Optional, Union

import anthropic
from anthropic import Anthropic
from flask import current_app

logger = logging.getLogger(__name__)

def get_anthropic_client() -> Anthropic:
    """
    Get an initialized Anthropic client
    
    Returns:
        Anthropic: Initialized Anthropic client
    """
    # Get API key from environment or config
    anthropic_key = current_app.config.get('ANTHROPIC_API_KEY')
    
    if not anthropic_key:
        logger.error("ANTHROPIC_API_KEY not set")
        raise ValueError("ANTHROPIC_API_KEY not set")
    
    # Initialize client
    return Anthropic(api_key=anthropic_key)

def generate_bill_summary(bill_text: str, bill_title: Optional[str] = None, 
                          summary_type: str = "general", length: str = "medium") -> Dict[str, Any]:
    """
    Generate a summary of a legislative bill using Claude
    
    Args:
        bill_text (str): The text of the bill
        bill_title (str, optional): The title of the bill
        summary_type (str): Type of summary - "general", "policy", "technical", "fiscal"
        length (str): Length of summary - "short", "medium", "long"
        
    Returns:
        dict: Summary data including the summary text and key provisions
    """
    client = get_anthropic_client()
    model = current_app.config.get('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
    
    # Prepare the prompt
    prompt = f"""You are an expert legal analyst for the Benton County Assessor's office. 
I need you to summarize this legislative bill that may affect property assessments.

{f"Bill Title: {bill_title}" if bill_title else ""}

Bill Text:
{bill_text}

Please provide a {length} {summary_type} summary of this bill. 
Focus on aspects relevant to property assessment, taxation, and valuation.
Also extract a list of 3-5 key provisions from the bill.

Respond in JSON format with these fields:
- summary: Your {summary_type} summary
- key_provisions: A list of the key provisions
- bill_type: The general category this bill falls under (e.g. "Property Tax", "Assessment Methodology", etc.)
"""

    try:
        # Make API call
        response = client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            system="You are an expert legal and policy analyst who specializes in property assessment legislation. You provide accurate, objective analysis in JSON format."
        )
        
        # Extract the response text
        response_text = response.content[0].text
        
        # Try to parse JSON from the response
        # Sometimes the model might include markdown code blocks or other formatting
        try:
            # First, try direct JSON parsing
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    # If that fails too, return a structured error response
                    logger.error("Failed to parse JSON from Claude response")
                    return {
                        "summary": "Error: Could not parse summary from AI response.",
                        "key_provisions": [],
                        "bill_type": "Unknown"
                    }
            else:
                # If no JSON-like structure is found, return a structured error
                logger.error("No JSON structure found in Claude response")
                return {
                    "summary": "Error: Could not extract summary from AI response.",
                    "key_provisions": [],
                    "bill_type": "Unknown"
                }
        
        return result
    except Exception as e:
        logger.exception(f"Error generating bill summary: {str(e)}")
        return {
            "summary": f"Error: {str(e)}",
            "key_provisions": [],
            "bill_type": "Unknown"
        }

def extract_bill_entities(bill_text: str, bill_title: Optional[str] = None, 
                          entity_types: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Extract named entities from a legislative bill using Claude
    
    Args:
        bill_text (str): The text of the bill
        bill_title (str, optional): The title of the bill
        entity_types (list, optional): Types of entities to extract
        
    Returns:
        dict: Extracted entities by type
    """
    client = get_anthropic_client()
    model = current_app.config.get('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
    
    # Default entity types if none provided
    if not entity_types:
        entity_types = [
            "organizations", 
            "people", 
            "locations", 
            "legal_references"
        ]
    
    # Prepare the prompt
    prompt = f"""You are an expert legal analyst for the Benton County Assessor's office. 
I need you to extract named entities from this legislative bill that may affect property assessments.

{f"Bill Title: {bill_title}" if bill_title else ""}

Bill Text:
{bill_text}

Please extract the following types of entities:
{", ".join(entity_types)}

For legal_references, include citations to laws, statutes, regulations, or other legal documents.

Respond in JSON format with each entity type as a field containing an array of unique entity names.
"""

    try:
        # Make API call
        response = client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            system="You are an expert legal and policy analyst who specializes in property assessment legislation. You provide accurate, objective entity extraction in JSON format."
        )
        
        # Extract the response text
        response_text = response.content[0].text
        
        # Try to parse JSON from the response
        try:
            # First, try direct JSON parsing
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    # If that fails too, return a structured error response
                    logger.error("Failed to parse JSON from Claude response")
                    return {entity_type: [] for entity_type in entity_types}
            else:
                # If no JSON-like structure is found, return a structured error
                logger.error("No JSON structure found in Claude response")
                return {entity_type: [] for entity_type in entity_types}
                
        # Ensure all requested entity types are present in the result
        for entity_type in entity_types:
            if entity_type not in result:
                result[entity_type] = []
                
        return result
    except Exception as e:
        logger.exception(f"Error extracting bill entities: {str(e)}")
        return {entity_type: [] for entity_type in entity_types}

def analyze_bill_impact(bill_text: str, bill_title: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze the impact of a legislative bill on property assessments using Claude
    
    Args:
        bill_text (str): The text of the bill
        bill_title (str, optional): The title of the bill
        
    Returns:
        dict: Impact analysis data
    """
    client = get_anthropic_client()
    model = current_app.config.get('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
    
    # Prepare the prompt
    prompt = f"""You are an expert property assessment analyst for the Benton County Assessor's office.
I need you to analyze the impact of this legislative bill on property assessments.

{f"Bill Title: {bill_title}" if bill_title else ""}

Bill Text:
{bill_text}

Please analyze:
1. How this bill would affect property assessment methodologies
2. Changes to property tax calculations or exemptions
3. Which specific property classes would be most affected (Residential, Commercial, Industrial, Agricultural, Vacant Land, Public)
4. Implementation requirements and timeline for the assessor's office

Respond in JSON format with these fields:
- summary: A concise summary of the overall impact
- impact_level: One of "High", "Medium", or "Low"
- affected_property_classes: An array of affected property classes
- property_impacts: An array of objects with "area" (aspect affected), "description" (description of impact), and "severity" (High, Medium, Low)
- implementation_timeline: Approximate timeline for implementation
"""

    try:
        # Make API call
        response = client.messages.create(
            model=model,
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            system="You are an expert property assessment analyst who specializes in analyzing the impacts of legislation on county assessment practices. You provide accurate, objective analysis in JSON format."
        )
        
        # Extract the response text
        response_text = response.content[0].text
        
        # Try to parse JSON from the response
        try:
            # First, try direct JSON parsing
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    # If that fails too, return a structured error response
                    logger.error("Failed to parse JSON from Claude response")
                    return {
                        "summary": "Error: Could not parse impact analysis from AI response.",
                        "impact_level": "Unknown",
                        "affected_property_classes": [],
                        "property_impacts": [],
                        "implementation_timeline": "Unknown"
                    }
            else:
                # If no JSON-like structure is found, return a structured error
                logger.error("No JSON structure found in Claude response")
                return {
                    "summary": "Error: Could not extract impact analysis from AI response.",
                    "impact_level": "Unknown",
                    "affected_property_classes": [],
                    "property_impacts": [],
                    "implementation_timeline": "Unknown"
                }
                
        # Ensure all expected fields are present
        required_fields = ["summary", "impact_level", "affected_property_classes", 
                          "property_impacts", "implementation_timeline"]
        for field in required_fields:
            if field not in result:
                if field == "property_impacts":
                    result[field] = []
                elif field == "affected_property_classes":
                    result[field] = []
                else:
                    result[field] = "Unknown"
                
        return result
    except Exception as e:
        logger.exception(f"Error analyzing bill impact: {str(e)}")
        return {
            "summary": f"Error: {str(e)}",
            "impact_level": "Unknown",
            "affected_property_classes": [],
            "property_impacts": [],
            "implementation_timeline": "Unknown"
        }