import re
import logging
from flask import current_app
from mcp.message_protocol import MCPMessage, MCPResponse

logger = logging.getLogger(__name__)

class DataValidationAgent:
    """
    Data Validation Agent
    
    Validates property data according to Washington State Department of Revenue guidelines.
    Performs checks on parcel ID format, address validity, value ranges, property classification,
    and data completeness.
    """
    
    def __init__(self):
        """Initialize the Data Validation Agent"""
        logger.info("Data Validation Agent initialized")
    
    def process_message(self, message):
        """
        Process a validation request
        
        Args:
            message (MCPMessage): The message containing property data to validate
            
        Returns:
            MCPResponse: Validation results
        """
        try:
            # Extract property data from the message
            property_data = message.get_value('property_data')
            if not property_data:
                return MCPResponse(
                    success=False, 
                    error="No property data provided for validation"
                )
            
            # Perform validation
            validation_results = self.validate_property_data(property_data)
            
            # Return the validation results
            return MCPResponse(
                success=not validation_results['has_errors'],
                data={
                    'validation_results': validation_results
                },
                error="Validation errors found" if validation_results['has_errors'] else None
            )
            
        except Exception as e:
            logger.exception(f"Error validating property data: {str(e)}")
            return MCPResponse(
                success=False,
                error=f"Error validating property data: {str(e)}"
            )
    
    def process_batch(self, message):
        """
        Process a batch validation request
        
        Args:
            message (MCPMessage): The message containing multiple property records to validate
            
        Returns:
            MCPResponse: Batch validation results
        """
        try:
            # Extract property data from the message
            properties = message.get_value('properties', [])
            if not properties:
                return MCPResponse(
                    success=False,
                    error="No properties provided for batch validation"
                )
            
            # Validate each property
            results = []
            for property_data in properties:
                validation = self.validate_property_data(property_data)
                results.append({
                    'property_data': property_data,
                    'validation_results': validation
                })
            
            # Check if any properties have validation errors
            has_errors = any(r['validation_results']['has_errors'] for r in results)
            
            # Return the batch validation results
            return MCPResponse(
                success=not has_errors,
                data={
                    'batch_results': results,
                    'summary': {
                        'total': len(results),
                        'valid': sum(1 for r in results if not r['validation_results']['has_errors']),
                        'invalid': sum(1 for r in results if r['validation_results']['has_errors'])
                    }
                },
                error="Some properties have validation errors" if has_errors else None
            )
            
        except Exception as e:
            logger.exception(f"Error in batch validation: {str(e)}")
            return MCPResponse(
                success=False,
                error=f"Error in batch validation: {str(e)}"
            )
    
    def validate_property_data(self, property_data):
        """
        Validate property data according to Washington State standards
        
        Args:
            property_data (dict): The property data to validate
            
        Returns:
            dict: Validation results
        """
        errors = []
        warnings = []
        
        # Get validation rules from config
        config = current_app.config
        parcel_id_pattern = config.get('PARCEL_ID_PATTERN', r'^\d{8}-\d{3}$')
        min_property_value = config.get('MIN_PROPERTY_VALUE', 1000.0)
        max_property_value = config.get('MAX_PROPERTY_VALUE', 1000000000.0)
        property_classes = config.get('PROPERTY_CLASSIFICATIONS', {})
        
        # Validate parcel ID format
        parcel_id = property_data.get('parcel_id')
        if not parcel_id:
            errors.append("Parcel ID is required")
        elif not re.match(parcel_id_pattern, parcel_id):
            errors.append(f"Invalid parcel ID format. Must match pattern: {parcel_id_pattern}")
        
        # Validate address
        address = property_data.get('property_address')
        if not address:
            errors.append("Property address is required")
        elif not address.endswith(('WA', 'Washington')):
            warnings.append("Property address should include Washington state")
        
        # Validate assessment year
        assessment_year = property_data.get('assessment_year')
        current_year = 2025  # Assuming current year for validation purposes
        if not assessment_year:
            errors.append("Assessment year is required")
        elif not isinstance(assessment_year, int):
            errors.append("Assessment year must be an integer")
        elif assessment_year < 2020 or assessment_year > current_year + 1:
            errors.append(f"Assessment year must be between 2020 and {current_year + 1}")
        
        # Validate assessed value
        assessed_value = property_data.get('assessed_value')
        if assessed_value is None:
            errors.append("Assessed value is required")
        elif not isinstance(assessed_value, (int, float)):
            errors.append("Assessed value must be a number")
        elif assessed_value < min_property_value:
            errors.append(f"Assessed value cannot be less than ${min_property_value:.2f}")
        elif assessed_value > max_property_value:
            errors.append(f"Assessed value cannot exceed ${max_property_value:.2f}")
        
        # Validate property class
        property_class = property_data.get('property_class')
        if not property_class:
            errors.append("Property class is required")
        elif property_class not in property_classes:
            valid_classes = ', '.join(property_classes.keys())
            errors.append(f"Invalid property class. Must be one of: {valid_classes}")
        
        # Check for completeness
        required_fields = ['parcel_id', 'property_address', 'assessment_year', 'assessed_value', 'property_class']
        missing_fields = [field for field in required_fields if field not in property_data or property_data.get(field) is None]
        if missing_fields:
            errors.append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Return the validation results
        return {
            'has_errors': len(errors) > 0,
            'has_warnings': len(warnings) > 0,
            'errors': errors,
            'warnings': warnings
        }
