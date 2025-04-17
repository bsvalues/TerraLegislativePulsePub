import logging
from flask import current_app
from mcp.message_protocol import MCPMessage, MCPResponse

logger = logging.getLogger(__name__)

class MasterControlProgram:
    """
    Master Control Program (MCP) for orchestrating AI agents and handling messages.
    This serves as the central hub for routing requests to the appropriate specialized agents.
    """
    
    def __init__(self):
        self.agents = {}
        self.agent_status = {}
        logger.info("MCP initialized")
    
    def register_agent(self, agent):
        """Register an agent with the MCP"""
        agent_type = agent.__class__.__name__
        self.agents[agent_type] = agent
        self.agent_status[agent_type] = 'active'
        logger.info(f"Agent registered: {agent_type}")
        return True
    
    def unregister_agent(self, agent_type):
        """Unregister an agent from the MCP"""
        if agent_type in self.agents:
            del self.agents[agent_type]
            del self.agent_status[agent_type]
            logger.info(f"Agent unregistered: {agent_type}")
            return True
        logger.warning(f"Attempted to unregister non-existent agent: {agent_type}")
        return False
    
    def get_status(self):
        """Get the status of all registered agents"""
        return {
            'mcp_status': 'active',
            'agents': self.agent_status
        }
    
    def route_message(self, message):
        """
        Route a message to the appropriate agent based on the message type
        
        Args:
            message (MCPMessage): The message to route
            
        Returns:
            MCPResponse: The response from the agent
        """
        try:
            message_type = message.get_type()
            
            # Route to the appropriate agent based on message type
            if message_type == 'property_validate':
                if 'DataValidationAgent' in self.agents:
                    return self.agents['DataValidationAgent'].process_message(message)
            
            elif message_type == 'property_value':
                if 'ValuationAgent' in self.agents:
                    return self.agents['ValuationAgent'].process_message(message)
            
            elif message_type == 'property_impact':
                if 'PropertyImpactAgent' in self.agents:
                    return self.agents['PropertyImpactAgent'].process_message(message)
            
            elif message_type == 'user_query':
                if 'UserInteractionAgent' in self.agents:
                    return self.agents['UserInteractionAgent'].process_message(message)
            
            # Handle batch operations
            elif message_type == 'batch_validate':
                if 'DataValidationAgent' in self.agents:
                    return self.agents['DataValidationAgent'].process_batch(message)
            
            # If we get here, either the message type was invalid or the required agent is not registered
            logger.error(f"Unable to route message of type {message_type}")
            return MCPResponse(success=False, data=None, error=f"No agent available to handle message type: {message_type}")
            
        except Exception as e:
            logger.exception(f"Error routing message: {str(e)}")
            return MCPResponse(success=False, data=None, error=f"Error routing message: {str(e)}")
    
    def process_api_request(self, endpoint, data):
        """
        Process an API request by creating an MCP message and routing it to the appropriate agent
        
        Args:
            endpoint (str): The API endpoint that was called
            data (dict): The request data
            
        Returns:
            dict: The response to send back to the client
        """
        try:
            # Map API endpoints to message types
            endpoint_to_type = {
                '/api/mcp/property-validate': 'property_validate',
                '/api/mcp/property-value': 'property_value',
                '/api/mcp/property-impact': 'property_impact',
                '/api/mcp/user-query': 'user_query',
                '/api/mcp/batch-validate': 'batch_validate'
            }
            
            message_type = endpoint_to_type.get(endpoint)
            if not message_type:
                return {
                    'success': False,
                    'error': f"Unknown endpoint: {endpoint}"
                }
            
            # Create a message from the request data
            message = MCPMessage(message_type, data)
            
            # Route the message to the appropriate agent
            response = self.route_message(message)
            
            # Return the response
            return {
                'success': response.success,
                'data': response.data,
                'error': response.error
            }
            
        except Exception as e:
            logger.exception(f"Error processing API request: {str(e)}")
            return {
                'success': False,
                'error': f"Error processing request: {str(e)}"
            }
