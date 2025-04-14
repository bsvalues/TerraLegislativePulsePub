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
        info = []
        
        # Get validation rules from config
        config = current_app.config
        parcel_id_pattern = config.get('PARCEL_ID_PATTERN', r'^\d{8}-\d{3}$')
        min_property_value = config.get('MIN_PROPERTY_VALUE', 1000.0)
        max_property_value = config.get('MAX_PROPERTY_VALUE', 1000000000.0)
        property_classes = config.get('PROPERTY_CLASSIFICATIONS', {})
        wa_state_code = config.get('WA_STATE_CODE', 'WA')
        benton_county_code = config.get('BENTON_COUNTY_CODE', '005')
        
        # Validate parcel ID format
        parcel_id = property_data.get('parcel_id')
        if not parcel_id:
            errors.append("Parcel ID is required")
        elif not re.match(parcel_id_pattern, parcel_id):
            errors.append(f"Invalid parcel ID format. Must match pattern: {parcel_id_pattern}")
        else:
            # Additional parcel ID validation for Washington state
            parts = parcel_id.split('-')
            if len(parts) == 2:
                # Check for Benton County specific format
                if len(parts[0]) == 8 and not parts[0].startswith(benton_county_code):
                    warnings.append(f"Parcel ID should start with Benton County code {benton_county_code}")
        
        # Validate property address
        address = property_data.get('property_address')
        city = property_data.get('property_city')
        state = property_data.get('property_state')
        zipcode = property_data.get('property_zip')
        
        # Address validation
        if not address:
            errors.append("Property address is required")
        elif len(address) < 5:
            errors.append("Property address is too short")
        elif not any(char.isdigit() for char in address):
            warnings.append("Property address should typically include a street number")
        
        # City validation
        if not city:
            errors.append("Property city is required")
        
        # State validation
        if not state:
            errors.append("Property state is required")
        elif state != wa_state_code:
            errors.append(f"Property must be located in Washington State ({wa_state_code})")
        
        # ZIP code validation
        if not zipcode:
            errors.append("Property ZIP code is required")
        elif not re.match(r'^\d{5}(-\d{4})?$', zipcode):
            errors.append("Invalid ZIP code format. Must be 5 digits or 5+4 digits (e.g., 99320 or 99320-1234)")
        # Benton County ZIP codes start with 993
        elif not zipcode.startswith('993'):
            warnings.append("ZIP code may not be in Benton County (should start with 993)")
        
        # Validate assessment year
        assessment_year = property_data.get('assessment_year')
        current_year = 2025  # Current year for validation purposes
        if not assessment_year:
            errors.append("Assessment year is required")
        elif not isinstance(assessment_year, int):
            try:
                assessment_year = int(assessment_year)
                info.append("Assessment year was converted from string to integer")
            except (ValueError, TypeError):
                errors.append("Assessment year must be an integer")
        
        if isinstance(assessment_year, int):
            if assessment_year < 2020:
                errors.append(f"Assessment year cannot be earlier than 2020")
            elif assessment_year > current_year + 1:
                errors.append(f"Assessment year cannot be later than {current_year + 1}")
            elif assessment_year < current_year:
                warnings.append(f"Assessment year {assessment_year} is in the past")
        
        # Validate property values
        assessed_value = property_data.get('assessed_value')
        land_value = property_data.get('land_value')
        improvement_value = property_data.get('improvement_value')
        
        # Assessed value validation
        if assessed_value is None:
            errors.append("Assessed value is required")
        elif not isinstance(assessed_value, (int, float)):
            try:
                assessed_value = float(assessed_value)
                info.append("Assessed value was converted from string to number")
            except (ValueError, TypeError):
                errors.append("Assessed value must be a number")
        
        if isinstance(assessed_value, (int, float)):
            if assessed_value < min_property_value:
                errors.append(f"Assessed value cannot be less than ${min_property_value:,.2f}")
            elif assessed_value > max_property_value:
                errors.append(f"Assessed value cannot exceed ${max_property_value:,.2f}")
        
        # Land value validation
        if land_value is not None:
            if not isinstance(land_value, (int, float)):
                try:
                    land_value = float(land_value)
                    info.append("Land value was converted from string to number")
                except (ValueError, TypeError):
                    errors.append("Land value must be a number")
            elif land_value < 0:
                errors.append("Land value cannot be negative")
            elif land_value > assessed_value:
                warnings.append("Land value exceeds total assessed value")
        
        # Improvement value validation
        if improvement_value is not None:
            if not isinstance(improvement_value, (int, float)):
                try:
                    improvement_value = float(improvement_value)
                    info.append("Improvement value was converted from string to number")
                except (ValueError, TypeError):
                    errors.append("Improvement value must be a number")
            elif improvement_value < 0:
                errors.append("Improvement value cannot be negative")
        
        # Check if land value + improvement value = assessed value (within tolerance)
        if (land_value is not None and improvement_value is not None and 
            isinstance(land_value, (int, float)) and isinstance(improvement_value, (int, float))):
            combined_value = land_value + improvement_value
            if abs(combined_value - assessed_value) > 1.0:  # Allow for small rounding differences
                warnings.append(f"Land value ({land_value:,.2f}) + improvement value ({improvement_value:,.2f}) " + 
                               f"should equal assessed value ({assessed_value:,.2f})")
        
        # Validate property class
        property_class = property_data.get('property_class')
        property_class_code = property_data.get('property_class_code')
        
        if not property_class:
            errors.append("Property class is required")
        elif property_class not in property_classes:
            valid_classes = ', '.join(property_classes.keys())
            errors.append(f"Invalid property class. Must be one of: {valid_classes}")
        
        # Validate property class code against the property class
        if property_class and property_class_code:
            valid_codes = property_classes.get(property_class, [])
            if property_class_code not in valid_codes:
                valid_codes_str = ', '.join(valid_codes)
                errors.append(f"Invalid property class code '{property_class_code}' for class {property_class}. " + 
                             f"Valid codes are: {valid_codes_str}")
        
        # Validate building characteristics for residential properties
        if property_class == 'Residential':
            # Bedrooms validation
            bedrooms = property_data.get('bedrooms')
            if bedrooms is not None:
                if not isinstance(bedrooms, int):
                    try:
                        bedrooms = int(bedrooms)
                        info.append("Bedrooms value was converted from string to integer")
                    except (ValueError, TypeError):
                        errors.append("Bedrooms must be an integer")
                elif bedrooms < 0:
                    errors.append("Bedrooms cannot be negative")
                elif bedrooms > 20:
                    warnings.append("Unusually high number of bedrooms")
            
            # Bathrooms validation
            bathrooms = property_data.get('bathrooms')
            if bathrooms is not None:
                if not isinstance(bathrooms, (int, float)):
                    try:
                        bathrooms = float(bathrooms)
                        info.append("Bathrooms value was converted from string to number")
                    except (ValueError, TypeError):
                        errors.append("Bathrooms must be a number")
                elif bathrooms < 0:
                    errors.append("Bathrooms cannot be negative")
                elif bathrooms > 20:
                    warnings.append("Unusually high number of bathrooms")
            
            # Year built validation
            year_built = property_data.get('year_built')
            if year_built is not None:
                if not isinstance(year_built, int):
                    try:
                        year_built = int(year_built)
                        info.append("Year built was converted from string to integer")
                    except (ValueError, TypeError):
                        errors.append("Year built must be an integer")
                elif year_built < 1850:
                    warnings.append("Year built seems unusually early")
                elif year_built > current_year:
                    errors.append(f"Year built cannot be in the future (current year: {current_year})")
        
        # Validate building characteristics for commercial properties
        if property_class == 'Commercial':
            # Building area validation
            building_area = property_data.get('building_area')
            if building_area is not None:
                if not isinstance(building_area, (int, float)):
                    try:
                        building_area = float(building_area)
                        info.append("Building area was converted from string to number")
                    except (ValueError, TypeError):
                        errors.append("Building area must be a number")
                elif building_area <= 0:
                    errors.append("Building area must be positive")
            
            # Validate commercial property specific fields
            if property_data.get('income_approach') == 'Yes':
                if not property_data.get('cap_rate'):
                    warnings.append("Capitalization rate should be provided for income approach")
                if not property_data.get('annual_income'):
                    warnings.append("Annual income should be provided for income approach")
        
        # Validate land area for all property types
        land_area = property_data.get('land_area')
        if land_area is not None:
            if not isinstance(land_area, (int, float)):
                try:
                    land_area = float(land_area)
                    info.append("Land area was converted from string to number")
                except (ValueError, TypeError):
                    errors.append("Land area must be a number")
            elif land_area <= 0:
                errors.append("Land area must be positive")
        
        # Check for required fields based on property class
        required_fields = ['parcel_id', 'property_address', 'property_city', 'property_state', 'property_zip', 
                          'assessment_year', 'assessed_value', 'property_class']
        
        # Add property-class specific required fields
        if property_class == 'Residential':
            required_fields.extend(['land_value', 'improvement_value', 'land_area'])
        elif property_class == 'Commercial':
            required_fields.extend(['land_value', 'improvement_value', 'land_area', 'building_area'])
        
        missing_fields = [field for field in required_fields if field not in property_data or property_data.get(field) is None]
        if missing_fields:
            errors.append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Ensure property data has a valuation method if it's an assessment
        if 'valuation_method' in property_data:
            valuation_method = property_data.get('valuation_method')
            valid_methods = config.get('VALUATION_METHODS', ['Market', 'Cost', 'Income'])
            if valuation_method not in valid_methods:
                errors.append(f"Invalid valuation method. Must be one of: {', '.join(valid_methods)}")
        
        # Return the validation results
        return {
            'has_errors': len(errors) > 0,
            'has_warnings': len(warnings) > 0,
            'errors': errors,
            'warnings': warnings,
            'info': info
        }
