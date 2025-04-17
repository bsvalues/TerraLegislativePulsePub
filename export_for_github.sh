#!/bin/bash

# Create a temporary directory for the export
mkdir -p github_export

# Copy all essential files
echo "Copying essential files..."
cp -r *.py github_export/
cp -r agents github_export/
cp -r mcp github_export/
cp -r routes github_export/
cp -r services github_export/
cp -r static github_export/
cp -r templates github_export/
cp -r utils github_export/

# Copy configuration files
echo "Copying configuration files..."
cp README.md github_export/
cp LICENSE github_export/
cp dependencies.txt github_export/rename_to_requirements.txt
cp .gitignore github_export/
cp GITHUB_SETUP.md github_export/

# Create a simplified config file with secret variables removed
echo "Creating a sanitized config.py file..."
cat > github_export/config.py << EOL
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
EOL

# Create a README in the export directory
echo "Creating export README..."
cat > github_export/README_FOR_EXPORT.md << EOL
# GitHub Export

This directory contains a clean export of the Benton County Assessor AI Platform code, ready for pushing to GitHub.

## Instructions

1. Copy all contents of this directory to a new location outside of Replit
2. Rename 'rename_to_requirements.txt' to 'requirements.txt'
3. Follow the steps in GITHUB_SETUP.md to create and push to your GitHub repository

## Note

This export has been sanitized to remove any sensitive information or Replit-specific files.
EOL

echo "Export completed successfully!"
echo "Files are available in the 'github_export' directory."
echo "Follow the instructions in 'github_export/README_FOR_EXPORT.md' to push to GitHub."