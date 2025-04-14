"""
Anthropic AI Service

This module provides functionality for interacting with the Anthropic Claude API.
It handles formatting prompts and processing responses for AI-assisted tasks.
"""

import os
import logging
import anthropic
from flask import current_app

logger = logging.getLogger(__name__)

def get_anthropic_client():
    """
    Get a configured Anthropic client instance.
    
    Returns:
        anthropic.Anthropic: Configured Anthropic client
    
    Raises:
        ValueError: If Anthropic API key is not configured
    """
    api_key = current_app.config.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("Anthropic API key not configured")
    
    return anthropic.Anthropic(api_key=api_key)

def get_ai_response(prompt, model=None, max_tokens=2000):
    """
    Get a response from the AI model for a given prompt.
    
    Args:
        prompt (str): The prompt to send to the AI model
        model (str, optional): The model to use. Defaults to config value.
        max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 2000.
    
    Returns:
        str: The AI-generated response
    
    Raises:
        Exception: If there's an error communicating with the Anthropic API
    """
    try:
        client = get_anthropic_client()
        
        # Use the model specified in the config if not provided
        if model is None:
            model = current_app.config.get('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
        
        # Format system prompt for the assessor context
        system_prompt = """You are an expert assistant for the Benton County Assessor's Office in Washington State.
Your role is to provide accurate, detailed analysis of legislative bills and their impact on property assessments.
Focus on objective, factual information, and cite specific sections of bills when possible.
Avoid political commentary and stick to assessment implications.
Structure your responses clearly with headings and bullet points when appropriate."""
        
        # Make the API call
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Extract and return the text content
        return response.content[0].text
        
    except Exception as e:
        logger.exception(f"Error getting AI response: {str(e)}")
        raise

def analyze_bill_impact(bill_text, bill_title, property_class=None, property_value=None):
    """
    Analyze how a legislative bill impacts property assessments.
    
    Args:
        bill_text (str): Full text of the bill
        bill_title (str): Title of the bill
        property_class (str, optional): Property class to focus on
        property_value (float, optional): Property value to consider
    
    Returns:
        dict: Structured analysis including impact, value change, implications
    
    Raises:
        Exception: If there's an error in processing
    """
    try:
        # Construct the prompt
        property_context = ""
        if property_class:
            property_context += f"\nFocus specifically on '{property_class}' class properties."
        if property_value:
            property_context += f"\nConsider implications for properties valued around ${property_value:,.2f}."
        
        prompt = f"""
        Analyze how this legislative bill impacts property assessments in Benton County, Washington:
        
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
        
        # In a real implementation, we would parse the response into a more structured format
        # For now, we'll return a simplified structure with the full text
        
        return {
            "impact_analysis": response_text,
            "success": True
        }
        
    except Exception as e:
        logger.exception(f"Error analyzing bill impact: {str(e)}")
        raise

def extract_bill_entities(bill_text, bill_title, entity_types=None):
    """
    Extract entities from a legislative bill.
    
    Args:
        bill_text (str): Full text of the bill
        bill_title (str): Title of the bill
        entity_types (list, optional): Types of entities to extract
    
    Returns:
        dict: Extracted entities grouped by type
    
    Raises:
        Exception: If there's an error in processing
    """
    try:
        # Default entity types if none provided
        if entity_types is None:
            entity_types = ["organization", "person", "location", "date", "money", "percentage"]
        
        # Construct the prompt
        prompt = f"""
        Extract the following types of entities from this legislative bill:
        {', '.join(entity_types)}
        
        Bill Title: {bill_title}
        
        Bill Text:
        {bill_text}
        
        For each entity found, provide:
        1. The exact text of the entity
        2. The entity type
        3. The context (sentence or clause where it appears)
        
        Format your response as a JSON object with each entity type as a key and a list of objects containing
        the entity text, type, and context.
        """
        
        # Get the AI response
        response_text = get_ai_response(prompt)
        
        # In a real implementation, we would parse the JSON in the response
        # For now, we'll return a simplified structure
        
        return {
            "extracted_entities": response_text,
            "entity_types": entity_types,
            "success": True
        }
        
    except Exception as e:
        logger.exception(f"Error extracting entities: {str(e)}")
        raise