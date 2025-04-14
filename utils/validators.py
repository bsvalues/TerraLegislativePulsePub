import re
import logging

logger = logging.getLogger(__name__)

def validate_request_data(data, required_fields):
    """
    Validate that required fields are present in the request data
    
    Args:
        data (dict): The request data to validate
        required_fields (list): List of required field names
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not data:
        return False, "No data provided"
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, None

def validate_email(email):
    """
    Validate email format
    
    Args:
        email (str): The email to validate
        
    Returns:
        bool: Whether the email is valid
    """
    if not email:
        return False
    
    # Simple regex for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_parcel_id(parcel_id, pattern=r'^\d{8}-\d{3}$'):
    """
    Validate parcel ID format
    
    Args:
        parcel_id (str): The parcel ID to validate
        pattern (str): Regex pattern to match
        
    Returns:
        bool: Whether the parcel ID is valid
    """
    if not parcel_id:
        return False
    
    return re.match(pattern, parcel_id) is not None

def validate_property_class(property_class, valid_classes):
    """
    Validate property classification
    
    Args:
        property_class (str): The property class to validate
        valid_classes (list): List of valid property classes
        
    Returns:
        bool: Whether the property class is valid
    """
    if not property_class:
        return False
    
    return property_class in valid_classes

def validate_numeric_value(value, min_value=None, max_value=None):
    """
    Validate numeric value
    
    Args:
        value: The value to validate
        min_value: Minimum allowed value (optional)
        max_value: Maximum allowed value (optional)
        
    Returns:
        bool: Whether the value is valid
    """
    try:
        # Convert to float if not already a number
        if not isinstance(value, (int, float)):
            value = float(value)
        
        # Check min value if provided
        if min_value is not None and value < min_value:
            return False
        
        # Check max value if provided
        if max_value is not None and value > max_value:
            return False
        
        return True
    except (ValueError, TypeError):
        return False
