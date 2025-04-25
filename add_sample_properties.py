"""
Add Sample Properties

This script adds sample property data to the database for testing purposes.
"""

import logging
from datetime import datetime, timedelta
from app import app
from bootstrap import db
from models import Property, Assessment

logger = logging.getLogger(__name__)

def add_sample_properties():
    """Add sample properties to the database"""
    with app.app_context():
        # Check if properties already exist
        existing_count = Property.query.count()
        if existing_count > 0:
            logger.info(f"{existing_count} properties already exist in the database")
            return
        
        # Sample residential properties
        sample_properties = [
            # Residential properties
            {
                'parcel_id': '12345678-001',
                'property_address': '123 Main Street',
                'property_city': 'Kennewick',
                'property_state': 'WA',
                'property_zip': '99336',
                'property_class': 'Residential',
                'land_area': 8500.0,
                'building_area': 2200.0,
                'year_built': 1995,
                'bedrooms': 4,
                'bathrooms': 2.5,
                'assessments': [
                    {
                        'assessment_year': 2024,
                        'assessed_value': 475000.0,
                        'land_value': 125000.0,
                        'improvement_value': 350000.0,
                        'market_value': 480000.0,
                        'valuation_method': 'Market',
                        'assessment_date': datetime.now() - timedelta(days=30)
                    }
                ]
            },
            {
                'parcel_id': '12345678-002',
                'property_address': '456 Oak Avenue',
                'property_city': 'Richland',
                'property_state': 'WA',
                'property_zip': '99352',
                'property_class': 'Residential',
                'land_area': 7200.0,
                'building_area': 1800.0,
                'year_built': 2005,
                'bedrooms': 3,
                'bathrooms': 2.0,
                'assessments': [
                    {
                        'assessment_year': 2024,
                        'assessed_value': 425000.0,
                        'land_value': 110000.0,
                        'improvement_value': 315000.0,
                        'market_value': 430000.0,
                        'valuation_method': 'Market',
                        'assessment_date': datetime.now() - timedelta(days=45)
                    }
                ]
            },
            # Commercial property
            {
                'parcel_id': '12345678-003',
                'property_address': '789 Business Way',
                'property_city': 'Kennewick',
                'property_state': 'WA',
                'property_zip': '99336',
                'property_class': 'Commercial',
                'land_area': 25000.0,
                'building_area': 15000.0,
                'year_built': 2010,
                'assessments': [
                    {
                        'assessment_year': 2024,
                        'assessed_value': 1250000.0,
                        'land_value': 350000.0,
                        'improvement_value': 900000.0,
                        'market_value': 1275000.0,
                        'valuation_method': 'Income',
                        'assessment_date': datetime.now() - timedelta(days=60)
                    }
                ]
            },
            # Industrial property
            {
                'parcel_id': '12345678-004',
                'property_address': '101 Industrial Park',
                'property_city': 'Richland',
                'property_state': 'WA',
                'property_zip': '99352',
                'property_class': 'Industrial',
                'land_area': 50000.0,
                'building_area': 35000.0,
                'year_built': 2000,
                'assessments': [
                    {
                        'assessment_year': 2024,
                        'assessed_value': 2750000.0,
                        'land_value': 750000.0,
                        'improvement_value': 2000000.0,
                        'market_value': 2800000.0,
                        'valuation_method': 'Cost',
                        'assessment_date': datetime.now() - timedelta(days=90)
                    }
                ]
            },
            # Agricultural property
            {
                'parcel_id': '12345678-005',
                'property_address': '5555 Rural Route',
                'property_city': 'Benton City',
                'property_state': 'WA',
                'property_zip': '99320',
                'property_class': 'Agricultural',
                'land_area': 800000.0,
                'year_built': 1975,
                'assessments': [
                    {
                        'assessment_year': 2024,
                        'assessed_value': 950000.0,
                        'land_value': 850000.0,
                        'improvement_value': 100000.0,
                        'market_value': 975000.0,
                        'valuation_method': 'Market',
                        'assessment_date': datetime.now() - timedelta(days=120)
                    }
                ]
            }
        ]
        
        try:
            # Add properties and assessments to the database
            for property_data in sample_properties:
                # Extract assessments data
                assessments_data = property_data.pop('assessments')
                
                # Create property
                new_property = Property(**property_data)
                db.session.add(new_property)
                db.session.flush()  # Flush to get the ID
                
                # Create assessments
                for assessment_data in assessments_data:
                    assessment_data['property_id'] = new_property.id
                    new_assessment = Assessment(**assessment_data)
                    db.session.add(new_assessment)
            
            # Commit all changes
            db.session.commit()
            logger.info(f"Added {len(sample_properties)} sample properties to the database")
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding sample properties: {str(e)}")
            raise e

if __name__ == "__main__":
    add_sample_properties()