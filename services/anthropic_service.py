"""
Anthropic Service

This module provides an interface to the Anthropic Claude API for AI-powered analysis.
"""

import os
import json
import logging
import sys
import re
from flask import current_app
import anthropic
from anthropic import Anthropic

logger = logging.getLogger(__name__)

def get_anthropic_client():
    """
    Get the Anthropic client instance
    
    Returns:
        Anthropic: The Anthropic client
    """
    # Get API key from app config
    anthropic_key = current_app.config.get('ANTHROPIC_API_KEY')
    
    if not anthropic_key:
        logger.error("Anthropic API key not found in configuration")
        return None
    
    try:
        # Initialize the client
        # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
        client = Anthropic(
            api_key=anthropic_key,
        )
        return client
    except Exception as e:
        logger.exception(f"Error initializing Anthropic client: {str(e)}")
        return None

def get_ai_response(prompt, max_tokens=2000, temperature=0.7):
    """
    Get a response from the AI using Anthropic Claude
    
    Args:
        prompt (str): The prompt to send to the AI
        max_tokens (int, optional): Maximum number of tokens in the response
        temperature (float, optional): Temperature for response generation
        
    Returns:
        str: The AI response
    """
    try:
        # Get the Anthropic client
        client = get_anthropic_client()
        
        if not client:
            return "Error: AI service not available"
        
        # Get model from config
        model = current_app.config.get('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
        
        # Call the API with system prompt for consistent responses
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system="You are an AI assistant for the Benton County Assessor's Office, specializing in property assessment and tax legislation analysis. Provide clear, objective, and accurate responses based on Washington State assessment laws and regulations. Format responses with clear sections and bullet points where appropriate.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the response text
        response_text = message.content[0].text
        
        # Clean up the response if needed
        if response_text.startswith("I'll provide"):
            # Remove common prefixes like "I'll provide..." or "Here's..."
            lines = response_text.split('\n')
            if len(lines) > 1:
                response_text = '\n'.join(lines[1:])
        
        return response_text
        
    except Exception as e:
        logger.exception(f"Error getting AI response: {str(e)}")
        return f"Error getting AI response: {str(e)}"

def extract_structured_data(prompt, extraction_format):
    """
    Extract structured data from the AI response
    
    Args:
        prompt (str): The prompt to send to the AI
        extraction_format (dict): The expected format for extraction
        
    Returns:
        dict: The extracted structured data
    """
    try:
        # Add format instructions to the prompt
        format_instructions = f"""
        Format your response as a JSON object with the following structure:
        {json.dumps(extraction_format, indent=2)}
        
        Only return the JSON object without additional text or explanation.
        """
        
        full_prompt = f"{prompt}\n\n{format_instructions}"
        
        # Get the AI response
        response_text = get_ai_response(full_prompt)
        
        # Extract JSON from the response
        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        json_match = re.search(json_pattern, response_text)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no code block is found, try to parse the whole response
            json_str = response_text
        
        # Parse the JSON
        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from AI response")
            return {"error": "Failed to parse structured data from AI response"}
        
    except Exception as e:
        logger.exception(f"Error extracting structured data: {str(e)}")
        return {"error": f"Error extracting structured data: {str(e)}"}