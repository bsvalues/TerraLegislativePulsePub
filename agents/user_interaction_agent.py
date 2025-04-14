import logging
from flask import current_app
from mcp.message_protocol import MCPMessage, MCPResponse
from services.anthropic_service import get_ai_response

logger = logging.getLogger(__name__)

class UserInteractionAgent:
    """
    User Interaction Agent
    
    Provides a natural language interface for assessor staff to:
    - Search for properties
    - Request valuations
    - Validate data
    - Get help and guidance
    """
    
    def __init__(self):
        """Initialize the User Interaction Agent"""
        logger.info("User Interaction Agent initialized")
    
    def process_message(self, message):
        """
        Process a user query
        
        Args:
            message (MCPMessage): The message containing the user query
            
        Returns:
            MCPResponse: Response to the user query
        """
        try:
            # Extract user query from the message
            user_query = message.get_value('query')
            if not user_query:
                return MCPResponse(
                    success=False,
                    error="No query provided"
                )
            
            # Get context from the message (if any)
            context = message.get_value('context', {})
            
            # Process the query
            response = self.process_query(user_query, context)
            
            # Return the response
            return MCPResponse(
                success=True,
                data=response
            )
            
        except Exception as e:
            logger.exception(f"Error processing user query: {str(e)}")
            return MCPResponse(
                success=False,
                error=f"Error processing user query: {str(e)}"
            )
    
    def process_query(self, query, context):
        """
        Process a natural language query
        
        Args:
            query (str): The user's query
            context (dict): Additional context for the query
            
        Returns:
            dict: The response to the query
        """
        try:
            # Analyze the query to determine intent
            intent = self.determine_intent(query)
            
            # Process the query based on intent
            if intent == 'property_search':
                return self.handle_property_search(query, context)
            elif intent == 'valuation_request':
                return self.handle_valuation_request(query, context)
            elif intent == 'data_validation':
                return self.handle_data_validation(query, context)
            elif intent == 'help_request':
                return self.handle_help_request(query, context)
            else:
                # Default to AI-assisted response for unknown intents
                return self.get_ai_assisted_response(query, context)
            
        except Exception as e:
            logger.exception(f"Error in query processing: {str(e)}")
            return {
                'response': f"I'm sorry, but I encountered an error while processing your query: {str(e)}",
                'intent': 'error',
                'confidence': 0.0
            }
    
    def determine_intent(self, query):
        """
        Determine the intent of a user query
        
        Args:
            query (str): The user's query
            
        Returns:
            str: The determined intent
        """
        # Simple keyword-based intent detection
        query = query.lower()
        
        if any(keyword in query for keyword in ['find', 'search', 'lookup', 'locate', 'get property']):
            return 'property_search'
        
        elif any(keyword in query for keyword in ['value', 'assess', 'worth', 'price', 'appraise']):
            return 'valuation_request'
        
        elif any(keyword in query for keyword in ['validate', 'check', 'verify', 'review']):
            return 'data_validation'
        
        elif any(keyword in query for keyword in ['help', 'guide', 'how to', 'instructions', 'explain']):
            return 'help_request'
        
        else:
            # Default intent for queries that don't match known patterns
            return 'general_inquiry'
    
    def handle_property_search(self, query, context):
        """
        Handle a property search query
        
        Args:
            query (str): The user's query
            context (dict): Additional context for the query
            
        Returns:
            dict: The response to the query
        """
        # In a real implementation, this would:
        # 1. Extract search parameters from the query
        # 2. Query the database for matching properties
        # 3. Format and return the results
        
        # For demonstration, we'll return a mock response
        return {
            'response': f"I'll search for properties based on: '{query}'",
            'intent': 'property_search',
            'confidence': 0.85,
            'search_parameters': {
                'query': query,
                'extracted_address': context.get('address', None),
                'extracted_parcel_id': context.get('parcel_id', None)
            },
            'search_results': []  # Would contain real search results in production
        }
    
    def handle_valuation_request(self, query, context):
        """
        Handle a valuation request query
        
        Args:
            query (str): The user's query
            context (dict): Additional context for the query
            
        Returns:
            dict: The response to the query
        """
        # In a real implementation, this would:
        # 1. Extract property information from the query
        # 2. Determine the valuation approach to use
        # 3. Call the Valuation Agent to perform the valuation
        # 4. Format and return the results
        
        # For demonstration, we'll return a mock response
        return {
            'response': f"I'll calculate the value for the property based on: '{query}'",
            'intent': 'valuation_request',
            'confidence': 0.85,
            'valuation_parameters': {
                'query': query,
                'property_id': context.get('property_id', None),
                'approach': 'market'  # Default approach
            },
            'valuation_results': None  # Would contain real valuation results in production
        }
    
    def handle_data_validation(self, query, context):
        """
        Handle a data validation query
        
        Args:
            query (str): The user's query
            context (dict): Additional context for the query
            
        Returns:
            dict: The response to the query
        """
        # In a real implementation, this would:
        # 1. Extract property information from the query
        # 2. Call the Data Validation Agent to validate the data
        # 3. Format and return the results
        
        # For demonstration, we'll return a mock response
        return {
            'response': f"I'll validate the property data for: '{query}'",
            'intent': 'data_validation',
            'confidence': 0.85,
            'validation_parameters': {
                'query': query,
                'property_id': context.get('property_id', None)
            },
            'validation_results': None  # Would contain real validation results in production
        }
    
    def handle_help_request(self, query, context):
        """
        Handle a help request query
        
        Args:
            query (str): The user's query
            context (dict): Additional context for the query
            
        Returns:
            dict: The response to the query
        """
        # Simple help system based on keywords
        query = query.lower()
        
        if 'property search' in query:
            return {
                'response': "To search for a property, you can ask me things like: 'Find property at 123 Main St' or 'Search for parcel ID 12345678-123'.",
                'intent': 'help_request',
                'confidence': 0.9,
                'help_topic': 'property_search'
            }
        
        elif 'valuation' in query:
            return {
                'response': "To get a property valuation, you can ask me things like: 'What is the value of 123 Main St?' or 'Calculate value for parcel 12345678-123 using the income approach'.",
                'intent': 'help_request',
                'confidence': 0.9,
                'help_topic': 'valuation'
            }
        
        elif 'validation' in query:
            return {
                'response': "To validate property data, you can ask me things like: 'Validate data for 123 Main St' or 'Check if parcel 12345678-123 meets standards'.",
                'intent': 'help_request',
                'confidence': 0.9,
                'help_topic': 'validation'
            }
        
        else:
            # General help
            return {
                'response': "I can help you with property searches, valuations, and data validation. Just ask me what you need!",
                'intent': 'help_request',
                'confidence': 0.9,
                'help_topic': 'general'
            }
    
    def get_ai_assisted_response(self, query, context):
        """
        Get an AI-assisted response using Claude
        
        Args:
            query (str): The user's query
            context (dict): Additional context for the query
            
        Returns:
            dict: The AI-assisted response
        """
        try:
            # Prepare the prompt for Claude
            system_prompt = """
            You are an AI assistant for the Benton County Assessor's Office in Washington State. 
            You help assessor staff with property assessments, valuations, and Washington State 
            property tax regulations. Answer questions concisely and accurately, focusing on 
            Benton County and Washington State property assessment practices. If you don't know 
            the answer, say so and suggest how the user might find the information.
            """
            
            # Prepare the user's query with context
            user_message = query
            if context:
                user_message += "\n\nContext: " + str(context)
            
            # Get response from Claude
            ai_response = get_ai_response(system_prompt, user_message)
            
            return {
                'response': ai_response,
                'intent': 'general_inquiry',
                'confidence': 0.7,
                'is_ai_generated': True
            }
            
        except Exception as e:
            logger.exception(f"Error getting AI-assisted response: {str(e)}")
            return {
                'response': "I'm sorry, but I'm having trouble generating a response right now. Please try again later.",
                'intent': 'error',
                'confidence': 0.0
            }
