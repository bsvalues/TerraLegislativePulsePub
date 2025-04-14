"""
Anthropic API Service

This module provides functionality for interacting with the Anthropic API.
"""

import os
import sys
import logging
import json
import re
from typing import Dict, Any, List, Tuple, Optional

import anthropic
from anthropic import Anthropic
from flask import current_app

logger = logging.getLogger(__name__)

def get_ai_response(prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 4000) -> str:
    """
    Get a response from the Anthropic API
    
    Args:
        prompt (str): The prompt to send to the API
        system_prompt (str, optional): The system prompt to use
        temperature (float): The temperature to use for generation
        max_tokens (int): The maximum number of tokens to generate
        
    Returns:
        str: The response from the API
    """
    try:
        # Get the API key
        api_key = current_app.config.get('ANTHROPIC_API_KEY')
        
        if not api_key:
            logger.error("Anthropic API key not configured")
            return "Error: Anthropic API key not configured"
        
        # Get the model
        model = current_app.config.get('ANTHROPIC_MODEL', "claude-3-5-sonnet-20241022")
        
        # Initialize the client
        client = Anthropic(
            api_key=api_key,
        )
        
        # Determine the message structure based on whether a system prompt is provided
        messages = []
        
        if system_prompt:
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        else:
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        
        # Call the API
        response = client.messages.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Return the response
        return response.content[0].text
        
    except Exception as e:
        logger.exception(f"Error getting AI response: {str(e)}")
        return f"Error: {str(e)}"

def analyze_bill_impact(bill_text: str, bill_title: Optional[str] = None, property_class: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze the impact of a bill on property assessments
    
    Args:
        bill_text (str): The text of the bill
        bill_title (str, optional): The title of the bill
        property_class (str, optional): The property class to analyze impact for
        
    Returns:
        Dict[str, Any]: The analysis results
    """
    try:
        # Build the prompt
        title_text = f"Title: {bill_title}\n\n" if bill_title else ""
        property_class_text = f"\nFocus specifically on implications for {property_class} properties." if property_class else ""
        
        prompt = f"""
        Analyze this legislative bill and its potential impact on property assessments and valuations:{property_class_text}
        
        {title_text}
        Bill Text:
        ```
        {bill_text[:10000]}
        ```
        
        Provide a comprehensive analysis covering:
        
        1. Key provisions that affect property assessment
        2. How valuation methodologies might need to change
        3. Specific impacts on tax calculations
        4. Implementation requirements and timeline
        5. Recommendations for county assessor offices
        
        Format your response in clear sections with headers for each of the above points.
        """
        
        # Get analysis from Claude
        system_prompt = "You are a property assessment expert working for a county assessor's office. You specialize in analyzing how legislative changes affect property assessments and valuations."
        
        response = get_ai_response(prompt, system_prompt, temperature=0.3)
        
        return {
            "success": True,
            "analysis": response,
            "bill_title": bill_title,
            "property_class": property_class
        }
        
    except Exception as e:
        logger.exception(f"Error analyzing bill impact: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def generate_bill_summary(bill_text: str, bill_title: Optional[str] = None, summary_length: str = "medium") -> Dict[str, Any]:
    """
    Generate a summary of a bill
    
    Args:
        bill_text (str): The text of the bill
        bill_title (str, optional): The title of the bill
        summary_length (str): The length of the summary (short, medium, long)
        
    Returns:
        Dict[str, Any]: The summary results
    """
    try:
        # Map summary length to word count
        word_counts = {
            "short": 150,
            "medium": 300,
            "long": 500
        }
        
        word_count = word_counts.get(summary_length, 300)
        
        # Build the prompt
        title_text = f"Title: {bill_title}\n\n" if bill_title else ""
        
        prompt = f"""
        Summarize this legislative bill related to property assessment and taxation:
        
        {title_text}
        Bill Text:
        ```
        {bill_text[:10000]}
        ```
        
        Please provide a {summary_length} summary (approximately {word_count} words) that captures:
        
        1. The main purpose and scope of the bill
        2. Key provisions that would affect property assessment
        3. Potential timeline and implementation considerations
        
        Focus on clarity and conciseness while ensuring all critical points are covered.
        """
        
        # Get summary from Claude
        system_prompt = "You are a legislative analyst for a county assessor's office. You specialize in summarizing bills related to property assessment and taxation."
        
        response = get_ai_response(prompt, system_prompt, temperature=0.3)
        
        return {
            "success": True,
            "summary": response,
            "bill_title": bill_title,
            "summary_length": summary_length,
            "word_count": len(response.split())
        }
        
    except Exception as e:
        logger.exception(f"Error generating bill summary: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def extract_entities(bill_text: str, bill_title: Optional[str] = None, entity_types: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Extract entities from a bill
    
    Args:
        bill_text (str): The text of the bill
        bill_title (str, optional): The title of the bill
        entity_types (List[str], optional): The types of entities to extract
        
    Returns:
        Dict[str, Any]: The extraction results
    """
    try:
        # Set default entity types if none provided
        if not entity_types:
            entity_types = ["organization", "person", "location", "date", "money", "property"]
        
        # Build the prompt
        title_text = f"Title: {bill_title}\n\n" if bill_title else ""
        
        prompt = f"""
        Extract the following entity types from this legislative bill:
        {', '.join(entity_types)}
        
        {title_text}
        Bill Text:
        ```
        {bill_text[:10000]}
        ```
        
        For each entity found, please provide:
        1. The entity text
        2. The entity type
        3. The context in which it appears (relevant sentence)
        
        Format the results as a JSON object with each entity type as a key and a list of extracted entities as the value.
        Each entity should be an object with keys for "text", "context", and any additional relevant information.
        
        Example format:
        {{
            "organization": [
                {{ "text": "Department of Revenue", "context": "The Department of Revenue shall establish guidelines..." }},
                ...
            ],
            "property": [
                {{ "text": "commercial real estate", "context": "Valuations for commercial real estate shall be adjusted..." }},
                ...
            ]
        }}
        """
        
        # Get entities from Claude
        system_prompt = "You are an entity extraction specialist for a county assessor's office. You extract relevant entities from legislative bills related to property assessment and taxation."
        
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
            entities = json.loads(json_str)
            return {
                "success": True,
                "entities": entities,
                "bill_title": bill_title,
                "entity_types": entity_types
            }
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing entities JSON: {str(e)}")
            return {
                "success": False,
                "error": f"Error parsing entities: {str(e)}",
                "raw_response": response
            }
        
    except Exception as e:
        logger.exception(f"Error extracting entities: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def summarize_bill(bill_text: str, bill_title: Optional[str] = None, summary_type: str = "general", length: str = "medium") -> Dict[str, Any]:
    """
    Generate a summary of a bill with specific focus
    
    Args:
        bill_text (str): The text of the bill
        bill_title (str, optional): The title of the bill
        summary_type (str): The type of summary (general, technical, public)
        length (str): The length of the summary (short, medium, long)
        
    Returns:
        Dict[str, Any]: The summary results
    """
    try:
        # Map summary length to word count
        word_counts = {
            "short": 150,
            "medium": 300,
            "long": 500
        }
        
        word_count = word_counts.get(length, 300)
        
        # Map summary type to audience/focus
        audience_guidance = {
            "general": "for a general audience with some knowledge of property assessment",
            "technical": "for technical staff with expertise in property assessment and taxation",
            "public": "for the general public with limited knowledge of property assessment processes"
        }
        
        audience = audience_guidance.get(summary_type, audience_guidance["general"])
        
        # Build the prompt
        title_text = f"Title: {bill_title}\n\n" if bill_title else ""
        
        prompt = f"""
        Summarize this legislative bill:
        
        {title_text}
        
        Please provide a {length} summary (approximately {word_count} words) {audience}.
        
        Bill Text:
        ```
        {bill_text[:10000]}
        ```
        """
        
        # Get summary from Claude
        system_prompt = "You are a legislative analyst for a county assessor's office. You specialize in summarizing bills related to property assessment and taxation for different audiences."
        
        response = get_ai_response(prompt, system_prompt, temperature=0.3)
        
        return {
            "success": True,
            "summary": response,
            "bill_title": bill_title,
            "summary_type": summary_type,
            "length": length,
            "word_count": len(response.split())
        }
        
    except Exception as e:
        logger.exception(f"Error generating bill summary: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Call this function to test the Anthropic API connection
def test_anthropic_connection() -> Dict[str, Any]:
    """
    Test the connection to the Anthropic API
    
    Returns:
        Dict[str, Any]: The test results
    """
    try:
        # Get the API key
        api_key = current_app.config.get('ANTHROPIC_API_KEY')
        
        if not api_key:
            logger.error("Anthropic API key not configured")
            return {
                "success": False,
                "error": "Anthropic API key not configured"
            }
        
        # Get the model
        model = current_app.config.get('ANTHROPIC_MODEL', "claude-3-5-sonnet-20241022")
        
        # Initialize the client
        client = Anthropic(
            api_key=api_key,
        )
        
        # Send a simple test request
        response = client.messages.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "Please respond with 'Connection successful!' if you can read this message."
                }
            ],
            max_tokens=50
        )
        
        # Check the response
        if "Connection successful" in response.content[0].text:
            return {
                "success": True,
                "message": "Connection to Anthropic API successful",
                "model": model
            }
        else:
            return {
                "success": True,
                "message": "Connection to Anthropic API successful, but unexpected response",
                "response": response.content[0].text,
                "model": model
            }
        
    except Exception as e:
        logger.exception(f"Error testing Anthropic connection: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }