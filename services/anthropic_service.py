import os
import logging
import sys
import anthropic
from anthropic import Anthropic

logger = logging.getLogger(__name__)

def get_anthropic_client():
    """
    Initialize and return an Anthropic API client.
    
    Returns:
        Anthropic: An initialized Anthropic client
    """
    # Get API key from environment variables
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if not anthropic_key:
        logger.error("ANTHROPIC_API_KEY environment variable must be set")
        return None
    
    try:
        # Initialize the client
        client = Anthropic(
            api_key=anthropic_key,
        )
        return client
    except Exception as e:
        logger.exception(f"Error initializing Anthropic client: {str(e)}")
        return None

def get_ai_response(system_prompt, user_message):
    """
    Get a response from the Anthropic Claude model.
    
    Args:
        system_prompt (str): The system prompt to provide context
        user_message (str): The user's message
        
    Returns:
        str: The AI-generated response
    """
    try:
        client = get_anthropic_client()
        if not client:
            return "Error: Unable to initialize AI client. Please check your API key."
        
        # Create a message with the Anthropic API
        # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000
        )
        
        # Extract and return the assistant's response
        return response.content[0].text
    
    except Exception as e:
        logger.exception(f"Error getting AI response: {str(e)}")
        return f"Error generating AI response: {str(e)}"
