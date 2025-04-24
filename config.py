import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'terra_legislative_pulse_default_key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Anthropic API configuration
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"  # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
    
    # External APIs
    LEGISCAN_API_KEY = os.environ.get('LEGISCAN_API_KEY')
    OPENSTATES_API_KEY = os.environ.get('OPENSTATES_API_KEY')
    
    # Washington State specific configuration
    WA_STATE_CODE = 'WA'
    WASHINGTON_COUNTY_CODE = '005'
    
    # Property validation rules
    PARCEL_ID_PATTERN = r'^\d{8}-\d{3}$'
    MIN_PROPERTY_VALUE = 1000.0
    MAX_PROPERTY_VALUE = 1000000000.0
    
    # Property classification codes as per WA state standards
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
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False

# Select the appropriate configuration
config = DevelopmentConfig if Config.DEBUG else ProductionConfig
