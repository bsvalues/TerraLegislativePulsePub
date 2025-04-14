class MCPMessage:
    """
    Standard message format for communication between the MCP and agents.
    """
    
    def __init__(self, message_type, data):
        """
        Initialize a new MCP message
        
        Args:
            message_type (str): The type of message (e.g., 'property_validate', 'property_value')
            data (dict): The message data
        """
        self.message_type = message_type
        self.data = data or {}
    
    def get_type(self):
        """Get the message type"""
        return self.message_type
    
    def get_data(self):
        """Get the message data"""
        return self.data
    
    def get_value(self, key, default=None):
        """
        Get a value from the message data
        
        Args:
            key (str): The key to retrieve
            default: The default value to return if the key is not found
            
        Returns:
            The value associated with the key, or the default value if not found
        """
        return self.data.get(key, default)

class MCPResponse:
    """
    Standard response format for communication between the MCP and agents.
    """
    
    def __init__(self, success, data=None, error=None):
        """
        Initialize a new MCP response
        
        Args:
            success (bool): Whether the operation was successful
            data (dict, optional): The response data
            error (str, optional): Error message, if any
        """
        self.success = success
        self.data = data
        self.error = error
    
    def to_dict(self):
        """
        Convert the response to a dictionary
        
        Returns:
            dict: The response as a dictionary
        """
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error
        }
