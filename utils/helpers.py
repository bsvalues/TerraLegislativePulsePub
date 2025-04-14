import logging
import json
from datetime import datetime, date

logger = logging.getLogger(__name__)

def format_currency(amount):
    """
    Format a number as currency
    
    Args:
        amount (float): The amount to format
        
    Returns:
        str: Formatted currency string
    """
    if amount is None:
        return "$0.00"
    
    try:
        return "${:,.2f}".format(float(amount))
    except (ValueError, TypeError):
        logger.warning(f"Could not format amount as currency: {amount}")
        return "$0.00"

def format_date(date_obj):
    """
    Format a date object as a string
    
    Args:
        date_obj (date or datetime): The date to format
        
    Returns:
        str: Formatted date string
    """
    if not date_obj:
        return ""
    
    try:
        if isinstance(date_obj, str):
            # Try to parse the string as a date
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
        
        return date_obj.strftime("%B %d, %Y")
    except Exception as e:
        logger.warning(f"Error formatting date: {str(e)}")
        return str(date_obj)

def truncate_text(text, max_length=100):
    """
    Truncate text to a maximum length and add ellipsis
    
    Args:
        text (str): The text to truncate
        max_length (int): Maximum length before truncation
        
    Returns:
        str: Truncated text
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + "..."

class JSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles dates and other special types
    """
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def to_json(data):
    """
    Convert data to JSON string with custom encoder
    
    Args:
        data: The data to convert
        
    Returns:
        str: JSON string
    """
    return json.dumps(data, cls=JSONEncoder)

def from_json(json_str):
    """
    Convert JSON string to Python object
    
    Args:
        json_str (str): The JSON string
        
    Returns:
        object: Python object
    """
    try:
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Error parsing JSON: {str(e)}")
        return None

def is_valid_assessment_year(year):
    """
    Check if an assessment year is valid
    
    Args:
        year (int): The year to check
        
    Returns:
        bool: Whether the year is valid
    """
    current_year = datetime.now().year
    
    # Assessment years are typically within a reasonable range of the current year
    # Allow current year and next year for upcoming assessments
    return year >= 2020 and year <= current_year + 1
