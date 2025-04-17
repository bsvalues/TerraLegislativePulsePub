"""
Configuration settings for the Benton County Assessor AI Platform.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'benton_county_assessor_default_key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API keys
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
    LEGISCAN_API_KEY = os.environ.get('LEGISCAN_API_KEY')
    OPENSTATES_API_KEY = os.environ.get('OPENSTATES_API_KEY')
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Property assessment settings
    WA_STATE_CODE = 'WA'
    BENTON_COUNTY_CODE = '005'
    
    # Data validation settings
    PARCEL_ID_PATTERN = r'^\d{8}-\d{3}$'
    MIN_PROPERTY_VALUE = 1000.0
    MAX_PROPERTY_VALUE = 1000000000.0
    
    # Property classifications
    PROPERTY_CLASSIFICATIONS = {
        'Residential': ['R1', 'R2', 'R3', 'R4'],
        'Commercial': ['C1', 'C2', 'C3'],
        'Industrial': ['I1', 'I2', 'I3'],
        'Agricultural': ['A1', 'A2'],
        'Vacant Land': ['V1', 'V2'],
        'Public': ['P1', 'P2']
    }
    
    # Valuation methods
    VALUATION_METHODS = ['Market', 'Cost', 'Income']
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
