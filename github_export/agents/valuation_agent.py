import logging
from flask import current_app
from mcp.message_protocol import MCPMessage, MCPResponse

logger = logging.getLogger(__name__)

class ValuationAgent:
    """
    Valuation Agent
    
    Calculates property values using multiple approaches as per Washington State standards:
    - Market comparison approach
    - Cost approach
    - Income approach (for commercial properties)
    """
    
    def __init__(self):
        """Initialize the Valuation Agent"""
        logger.info("Valuation Agent initialized")
    
    def process_message(self, message):
        """
        Process a valuation request
        
        Args:
            message (MCPMessage): The message containing property data for valuation
            
        Returns:
            MCPResponse: Valuation results
        """
        try:
            # Extract property data from the message
            property_data = message.get_value('property_data')
            if not property_data:
                return MCPResponse(
                    success=False,
                    error="No property data provided for valuation"
                )
            
            # Extract the requested valuation approach
            approach = message.get_value('valuation_approach', 'market')
            
            # Validate the approach
            valid_approaches = ['market', 'cost', 'income']
            if approach not in valid_approaches:
                return MCPResponse(
                    success=False,
                    error=f"Invalid valuation approach. Must be one of: {', '.join(valid_approaches)}"
                )
            
            # Perform valuation based on the requested approach
            valuation_result = None
            if approach == 'market':
                valuation_result = self.market_approach(property_data)
            elif approach == 'cost':
                valuation_result = self.cost_approach(property_data)
            elif approach == 'income':
                valuation_result = self.income_approach(property_data)
            
            # Check if valuation was successful
            if valuation_result is None:
                return MCPResponse(
                    success=False,
                    error=f"Failed to calculate valuation using {approach} approach"
                )
            
            # Return the valuation results
            return MCPResponse(
                success=True,
                data={
                    'valuation_results': valuation_result,
                    'approach': approach
                }
            )
            
        except Exception as e:
            logger.exception(f"Error in property valuation: {str(e)}")
            return MCPResponse(
                success=False,
                error=f"Error in property valuation: {str(e)}"
            )
    
    def market_approach(self, property_data):
        """
        Calculate property value using the market comparison approach
        
        Args:
            property_data (dict): The property data
            
        Returns:
            dict: Valuation results
        """
        try:
            # In a real implementation, this would:
            # 1. Query for comparable properties from database
            # 2. Apply adjustments for differences
            # 3. Calculate the final value
            
            # Extract property data
            base_value = property_data.get('assessed_value', 0)
            property_class = property_data.get('property_class', 'Residential')
            property_address = property_data.get('property_address', '')
            property_city = property_data.get('property_city', 'Kennewick')
            year_built = property_data.get('year_built')
            bedrooms = property_data.get('bedrooms')
            bathrooms = property_data.get('bathrooms')
            building_area = property_data.get('building_area')
            land_area = property_data.get('land_area')
            
            # Location factor based on city
            location_factors = {
                'Kennewick': 1.02,
                'Richland': 1.03,
                'West Richland': 1.04,
                'Prosser': 0.95,
                'Benton City': 0.93
            }
            
            # Apply market multipliers based on property class
            class_multipliers = {
                'Residential': 1.05,  # 5% appreciation for residential
                'Commercial': 1.03,   # 3% appreciation for commercial
                'Industrial': 1.02,   # 2% appreciation for industrial
                'Agricultural': 1.01, # 1% appreciation for agricultural
                'Vacant Land': 1.04,  # 4% appreciation for vacant land
                'Public': 1.00        # No appreciation for public properties
            }
            
            # Generate some comparable properties (for demonstration)
            comparables = []
            confidence_adjustments = []
            
            # Calculate market adjustments
            market_multiplier = class_multipliers.get(property_class, 1.0)
            location_multiplier = location_factors.get(property_city, 1.0)
            
            # Age adjustment for properties (newer properties have higher values)
            age_adjustment = 1.0
            current_year = 2025
            if year_built and isinstance(year_built, int):
                age = current_year - year_built
                if age <= 5:  # New construction premium
                    age_adjustment = 1.10
                elif age <= 10:
                    age_adjustment = 1.05
                elif age <= 20:
                    age_adjustment = 1.0
                elif age <= 40:
                    age_adjustment = 0.95
                else:
                    age_adjustment = 0.90
                
                # Add comparable with similar age
                comparable_year = year_built + (1 if age <= 10 else -2)
                comparable_value = base_value * (0.97 if age <= 10 else 1.03)
                comparables.append({
                    'address': f"{property_city} comparable (built {comparable_year})",
                    'year_built': comparable_year,
                    'value': comparable_value,
                    'adjustment_factor': 1.0 if age <= 10 else -1.0,
                    'adjusted_value': comparable_value * (1.0 if age <= 10 else 0.99)
                })
                confidence_adjustments.append(0.92)
            
            # Size adjustment for properties
            size_adjustment = 1.0
            if building_area and isinstance(building_area, (int, float)) and building_area > 0:
                if building_area < 1000:
                    size_adjustment = 0.95
                elif building_area < 1500:
                    size_adjustment = 0.98
                elif building_area < 2500:
                    size_adjustment = 1.0
                elif building_area < 3500:
                    size_adjustment = 1.03
                else:
                    size_adjustment = 1.05
                
                # Add comparable with similar size
                comparable_size = building_area * 0.9
                comparable_value = base_value * 0.95
                comparables.append({
                    'address': f"{property_city} comparable ({int(comparable_size)} sq ft)",
                    'building_area': comparable_size,
                    'value': comparable_value,
                    'adjustment_factor': size_adjustment,
                    'adjusted_value': comparable_value * size_adjustment
                })
                confidence_adjustments.append(0.9)
            
            # Feature adjustments for residential properties
            feature_adjustment = 1.0
            if property_class == 'Residential':
                if bedrooms and bathrooms:
                    # Calculate feature adjustment based on bedrooms and bathrooms
                    if bedrooms >= 4 and bathrooms >= 2.5:
                        feature_adjustment = 1.08  # Premium for large homes
                    elif bedrooms >= 3 and bathrooms >= 2:
                        feature_adjustment = 1.04
                    
                    # Add comparable with similar features
                    comparable_beds = bedrooms - 1 if bedrooms > 2 else bedrooms
                    comparable_baths = bathrooms - 0.5 if bathrooms > 1.5 else bathrooms
                    comparable_value = base_value * 0.92
                    comparables.append({
                        'address': f"{property_city} comparable ({comparable_beds} bed/{comparable_baths} bath)",
                        'bedrooms': comparable_beds,
                        'bathrooms': comparable_baths,
                        'value': comparable_value,
                        'adjustment_factor': feature_adjustment,
                        'adjusted_value': comparable_value * feature_adjustment
                    })
                    confidence_adjustments.append(0.88)
            
            # Calculate final market value with all adjustments
            market_value = base_value * market_multiplier * location_multiplier * age_adjustment * size_adjustment * feature_adjustment
            
            # Add one more comparable that's very close to our final valuation
            comparables.append({
                'address': f"Nearest comparable in {property_city}",
                'value': market_value * 0.98,
                'adjustment_factor': 1.02,
                'adjusted_value': market_value * 0.98 * 1.02
            })
            confidence_adjustments.append(0.95)
            
            # Calculate confidence score based on data completeness and comparable quality
            base_confidence = 0.85
            if len(comparables) >= 3:
                confidence_score = base_confidence * (sum(confidence_adjustments) / len(confidence_adjustments))
            else:
                confidence_score = base_confidence * 0.8  # Reduce confidence if fewer comparables
            
            # Ensure confidence is within bounds
            confidence_score = min(0.95, max(0.6, confidence_score))
            
            # Create detailed results
            return {
                'market_value': round(market_value, 2),
                'base_value': base_value,
                'market_multiplier': market_multiplier,
                'location_multiplier': location_multiplier,
                'age_adjustment': age_adjustment,
                'size_adjustment': size_adjustment,
                'feature_adjustment': feature_adjustment,
                'property_class': property_class,
                'property_city': property_city,
                'comparable_properties': comparables,
                'methodology': 'market_comparison',
                'confidence_score': round(confidence_score, 2)
            }
        
        except Exception as e:
            logger.exception(f"Error in market approach valuation: {str(e)}")
            raise
    
    def cost_approach(self, property_data):
        """
        Calculate property value using the cost approach
        
        Args:
            property_data (dict): The property data
            
        Returns:
            dict: Valuation results
        """
        try:
            # In a real implementation, this would:
            # 1. Calculate replacement cost of improvements
            # 2. Subtract depreciation
            # 3. Add land value
            
            # Extract property data
            base_value = property_data.get('assessed_value', 0)
            property_class = property_data.get('property_class', 'Residential')
            property_city = property_data.get('property_city', 'Kennewick')
            year_built = property_data.get('year_built', 2000)
            building_area = property_data.get('building_area', 1500)
            land_area = property_data.get('land_area', 5000)
            bedrooms = property_data.get('bedrooms')
            bathrooms = property_data.get('bathrooms')
            
            # Calculate age and depreciation
            current_year = 2025  # Current year for demonstration
            age = current_year - year_built
            
            # Calculate different depreciation rates based on property type and quality
            if property_class == 'Residential':
                # Residential properties depreciate differently
                if age <= 7:  # Newer homes depreciate slower
                    depreciation_rate = age * 0.005  # 0.5% per year for first 7 years
                elif age <= 20:
                    depreciation_rate = 0.035 + ((age - 7) * 0.01)  # 1% per year after first 7 years
                else:
                    depreciation_rate = 0.035 + 0.13 + ((age - 20) * 0.005)  # 0.5% per year after 20 years
            else:
                # Commercial and other properties
                depreciation_rate = min(0.6, age * 0.015)  # 1.5% per year, max 60%
            
            # Cap the depreciation rate
            depreciation_rate = min(0.7, depreciation_rate)  # Max 70% depreciation
            
            # Calculate quality factor based on available amenities (for residential)
            quality_factor = 1.0
            if property_class == 'Residential':
                # Quality adjustments based on bedrooms and bathrooms
                if bedrooms and bathrooms:
                    bed_bath_ratio = bathrooms / bedrooms if bedrooms > 0 else 0
                    if bed_bath_ratio >= 1.0 and bedrooms >= 3:
                        quality_factor = 1.15  # Premium for luxury homes
                    elif bed_bath_ratio >= 0.75 and bedrooms >= 3:
                        quality_factor = 1.08  # Above average
                    elif bed_bath_ratio >= 0.5:
                        quality_factor = 1.0   # Average
                    else:
                        quality_factor = 0.95  # Below average
            
            # Calculate component values based on property type
            if property_class == 'Residential':
                replacement_cost_per_sqft = 225.0 * quality_factor  # Base residential construction cost per sq ft
            elif property_class == 'Commercial':
                replacement_cost_per_sqft = 180.0  # Commercial construction cost
            elif property_class == 'Industrial':
                replacement_cost_per_sqft = 150.0  # Industrial construction cost
            else:
                replacement_cost_per_sqft = 100.0  # Default for other property types
            
            # Land value per square foot based on location
            land_value_factors = {
                'Kennewick': 12.0,
                'Richland': 14.0,
                'West Richland': 13.0,
                'Prosser': 8.0,
                'Benton City': 7.0
            }
            land_value_per_sqft = land_value_factors.get(property_city, 10.0)
            
            # Adjust land value based on property type
            if property_class == 'Commercial':
                land_value_per_sqft *= 1.5  # Commercial land is more valuable
            elif property_class == 'Agricultural':
                land_value_per_sqft *= 0.2  # Agricultural land is less valuable per sq ft
            
            # Calculate component values
            replacement_cost = building_area * replacement_cost_per_sqft
            depreciated_cost = replacement_cost * (1 - depreciation_rate)
            land_value = land_area * land_value_per_sqft
            
            # Calculate functional obsolescence (additional value reduction for outdated features)
            functional_obsolescence = 0.0
            if age > 30:
                functional_obsolescence = depreciated_cost * 0.05  # 5% reduction for outdated features
            
            # Calculate external obsolescence (market conditions)
            external_obsolescence = 0.0
            
            # Total cost approach value
            cost_value = depreciated_cost - functional_obsolescence - external_obsolescence + land_value
            
            # Calculate confidence score
            confidence_factors = []
            
            # Confidence based on data completeness
            if building_area and land_area and year_built:
                confidence_factors.append(0.9)  # High confidence with complete data
            elif building_area and year_built:
                confidence_factors.append(0.75)  # Medium confidence with partial data
            else:
                confidence_factors.append(0.6)  # Low confidence with minimal data
                
            # Confidence based on property age
            if age < 20:
                confidence_factors.append(0.85)  # Higher confidence for newer properties
            elif age < 40:
                confidence_factors.append(0.75)  # Medium confidence for middle-aged properties
            else:
                confidence_factors.append(0.65)  # Lower confidence for older properties
                
            # Calculate final confidence score
            confidence_score = sum(confidence_factors) / len(confidence_factors)
            confidence_score = min(0.9, max(0.6, confidence_score))  # Ensure within bounds
            
            # Create detailed results
            return {
                'cost_value': round(cost_value, 2),
                'replacement_cost': round(replacement_cost, 2),
                'depreciated_cost': round(depreciated_cost, 2),
                'land_value': round(land_value, 2),
                'functional_obsolescence': round(functional_obsolescence, 2),
                'external_obsolescence': round(external_obsolescence, 2),
                'depreciation_rate': round(depreciation_rate, 3),
                'building_age': age,
                'building_area': building_area,
                'land_area': land_area,
                'quality_factor': quality_factor,
                'replacement_cost_per_sqft': replacement_cost_per_sqft,
                'land_value_per_sqft': land_value_per_sqft,
                'property_class': property_class,
                'property_city': property_city,
                'methodology': 'cost_approach',
                'confidence_score': round(confidence_score, 2)
            }
        
        except Exception as e:
            logger.exception(f"Error in cost approach valuation: {str(e)}")
            raise
    
    def income_approach(self, property_data):
        """
        Calculate property value using the income approach (for commercial properties)
        
        Args:
            property_data (dict): The property data
            
        Returns:
            dict: Valuation results
        """
        try:
            # In a real implementation, this would:
            # 1. Estimate potential gross income
            # 2. Subtract vacancy and collection losses
            # 3. Subtract operating expenses
            # 4. Apply capitalization rate
            
            # Extract property data
            property_class = property_data.get('property_class', 'Residential')
            property_city = property_data.get('property_city', 'Kennewick')
            building_area = property_data.get('building_area', 1500)
            year_built = property_data.get('year_built', 2000)
            cap_rate_override = property_data.get('cap_rate')
            annual_income_override = property_data.get('annual_income')
            
            # Check if applicable for income approach
            if property_class not in ['Commercial', 'Industrial']:
                return {
                    'income_value': None,
                    'error': 'Income approach is only applicable for Commercial and Industrial properties',
                    'methodology': 'income_approach',
                    'confidence_score': 0.0
                }
            
            # Calculate age effect on income potential
            current_year = 2025
            age = current_year - year_built
            age_factor = 1.0
            if age < 5:
                age_factor = 1.1  # Premium for new buildings
            elif age < 15:
                age_factor = 1.0  # Standard rate
            elif age < 30:
                age_factor = 0.9  # Slightly reduced
            else:
                age_factor = 0.8  # Significantly reduced
            
            # Calculate location effect on rental rates
            location_factors = {
                'Kennewick': 1.0,    # Base city
                'Richland': 1.05,    # Premium city
                'West Richland': 1.02,
                'Prosser': 0.85,
                'Benton City': 0.8
            }
            location_factor = location_factors.get(property_city, 1.0)
            
            # Calculate rental rates based on property class, location, and age
            if property_class == 'Commercial':
                base_rental_rate = 18.0  # Base rate per sq ft
                if building_area > 10000:
                    base_rental_rate *= 0.85  # Bulk discount for large spaces
                elif building_area < 2000:
                    base_rental_rate *= 1.1  # Premium for small spaces
            elif property_class == 'Industrial':
                base_rental_rate = 12.0  # Base rate
                if building_area > 15000:
                    base_rental_rate *= 0.8  # Bulk discount for large industrial spaces
            else:
                base_rental_rate = 15.0  # Default fallback
            
            # Apply factors to get actual rental rate
            rental_rate_per_sqft = base_rental_rate * location_factor * age_factor
            
            # Calculate vacancy based on property type and location
            base_vacancy_rate = 0.05  # 5% base vacancy
            if property_class == 'Commercial':
                if location_factor < 0.9:
                    base_vacancy_rate = 0.08  # Higher vacancy in less desirable areas
                elif location_factor > 1.03:
                    base_vacancy_rate = 0.03  # Lower vacancy in premium areas
            else:  # Industrial
                if building_area > 10000:
                    base_vacancy_rate = 0.07  # Higher vacancy for large industrial
                else:
                    base_vacancy_rate = 0.04  # Lower vacancy for small industrial
            
            # Calculate expense ratio based on property type and age
            base_expense_ratio = 0.35  # 35% base expenses
            if age > 30:
                base_expense_ratio += 0.1  # Older buildings have higher expenses
            elif age < 10:
                base_expense_ratio -= 0.05  # Newer buildings have lower expenses
            
            if property_class == 'Industrial':
                base_expense_ratio += 0.05  # Industrial typically has higher expenses
            
            # Calculate capitalization rate based on property type, location, and market factors
            base_cap_rate = 0.07  # 7% base cap rate
            if property_class == 'Commercial':
                if location_factor > 1.03:
                    base_cap_rate = 0.065  # Lower cap rate (higher value) for premium locations
                elif location_factor < 0.9:
                    base_cap_rate = 0.075  # Higher cap rate (lower value) for less desirable locations
            elif property_class == 'Industrial':
                base_cap_rate = 0.08  # Industrial generally has higher cap rates
            
            # Use overrides if provided
            cap_rate = cap_rate_override / 100 if cap_rate_override else base_cap_rate
            
            # Calculate income
            potential_gross_income = building_area * rental_rate_per_sqft
            if annual_income_override:
                # If annual income is provided, use it instead of calculated value
                potential_gross_income = annual_income_override
                
            effective_gross_income = potential_gross_income * (1 - base_vacancy_rate)
            net_operating_income = effective_gross_income * (1 - base_expense_ratio)
            income_value = net_operating_income / cap_rate
            
            # Calculate confidence score based on data completeness
            confidence_factors = []
            
            # Check if we have all key data points
            if building_area and year_built:
                confidence_factors.append(0.85)
            else:
                confidence_factors.append(0.7)
                
            # Higher confidence with direct income data
            if annual_income_override:
                confidence_factors.append(0.9)
            else:
                confidence_factors.append(0.75)
                
            # Higher confidence with provided cap rate
            if cap_rate_override:
                confidence_factors.append(0.9)
            else:
                confidence_factors.append(0.8)
                
            # Calculate final confidence score
            confidence_score = sum(confidence_factors) / len(confidence_factors)
            confidence_score = min(0.9, max(0.6, confidence_score))
            
            # Create detailed results
            return {
                'income_value': round(income_value, 2),
                'potential_gross_income': round(potential_gross_income, 2),
                'effective_gross_income': round(effective_gross_income, 2),
                'net_operating_income': round(net_operating_income, 2),
                'vacancy_rate': base_vacancy_rate,
                'expense_ratio': base_expense_ratio,
                'cap_rate': cap_rate,
                'building_area': building_area,
                'rental_rate_per_sqft': round(rental_rate_per_sqft, 2),
                'age_factor': age_factor,
                'location_factor': location_factor,
                'property_class': property_class,
                'property_city': property_city,
                'building_age': age,
                'methodology': 'income_approach',
                'confidence_score': round(confidence_score, 2)
            }
        
        except Exception as e:
            logger.exception(f"Error in income approach valuation: {str(e)}")
            raise
