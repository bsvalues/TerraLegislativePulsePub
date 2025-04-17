"""
Message Protocol for the Master Control Program

This module defines the message format for communication between components in the
Benton County Assessor AI Platform.
"""

class MCPMessage:
    """
    Message class for communication between components in the AI platform
    
    Attributes:
        type (str): The type of message (e.g., 'property_validation', 'property_valuation')
        sender (str): The sender of the message
        values (dict): The data values contained in the message
    """
    
    def __init__(self, message_type, sender='system', data=None):
        """
        Initialize a new MCP message
        
        Args:
            message_type (str): The type of message
            sender (str): The sender of the message (default: 'system')
            data (dict): The data values contained in the message (default: {})
        """
        self.type = message_type
        self.sender = sender
        self.values = data or {}
        self.timestamp = None  # Will be set when the message is processed
    
    def __str__(self):
        """Return a string representation of the message"""
        return f"MCPMessage(type={self.type}, sender={self.sender}, values={self.values})"


class MCPResponse:
    """
    Response class for communication between components in the AI platform
    
    Attributes:
        success (bool): Whether the operation was successful
        data (dict): The data returned by the operation
        error (str): Error message if the operation failed
    """
    
    def __init__(self, success=True, data=None, error=None):
        """
        Initialize a new MCP response
        
        Args:
            success (bool): Whether the operation was successful (default: True)
            data (dict): The data returned by the operation (default: {})
            error (str): Error message if the operation failed (default: None)
        """
        self.success = success
        self.data = data or {}
        self.error = error
    
    def __str__(self):
        """Return a string representation of the response"""
        if self.success:
            return f"MCPResponse(success=True, data={self.data})"
        else:
            return f"MCPResponse(success=False, error={self.error})"