#!/usr/bin/env python3
"""
GitHub Export Structure Checker

This script checks that all necessary files and directories are present
in the GitHub export. Run this after downloading to make sure everything
is in the right place.
"""

import os
import sys

# Expected directories
EXPECTED_DIRS = [
    'agents',
    'mcp',
    'routes',
    'services',
    'static',
    'templates',
    'utils',
    'static/css',
    'static/images',
    'static/js',
]

# Expected key files
EXPECTED_FILES = [
    'main.py',
    'app.py',
    'models.py',
    'config.py',
    'scheduler.py',
    'README.md',
    'LICENSE',
    '.gitignore',
    'requirements.txt',  # Renamed from rename_to_requirements.txt
    'templates/base.html',
    'templates/index.html',
    'templates/bills.html',
    'templates/property_impact.html',
    'routes/web.py',
    'services/trackers/wa_legislature.py',
    'agents/data_validation_agent.py',
    'agents/property_impact_agent.py',
    'agents/user_interaction_agent.py',
]

def check_structure():
    """Check that the GitHub export structure is correct"""
    errors = []
    warnings = []
    
    # Check current directory
    current_dir = os.path.basename(os.getcwd())
    if current_dir != 'github_export' and 'benton' not in current_dir.lower():
        warnings.append(f"WARNING: Current directory '{current_dir}' doesn't seem to be the GitHub export. Make sure you're in the right directory.")
    
    # Check directories
    for directory in EXPECTED_DIRS:
        if not os.path.isdir(directory):
            errors.append(f"ERROR: Directory '{directory}' is missing.")
    
    # Check key files
    for file_path in EXPECTED_FILES:
        if not os.path.isfile(file_path):
            if file_path == 'requirements.txt' and os.path.isfile('rename_to_requirements.txt'):
                warnings.append("WARNING: 'rename_to_requirements.txt' needs to be renamed to 'requirements.txt'.")
            else:
                errors.append(f"ERROR: File '{file_path}' is missing.")
    
    # Report results
    if not errors and not warnings:
        print("✅ All checks passed! The GitHub export structure is correct.")
        return True
    
    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if errors:
        print("\n❌ Errors found:")
        for error in errors:
            print(f"  - {error}")
        print("\nThe GitHub export structure is NOT correct. Please fix the issues above before continuing.")
        return False
    
    print("\n⚠️  The GitHub export structure has some warnings, but no errors.")
    return True

if __name__ == "__main__":
    print("Checking GitHub export structure...")
    success = check_structure()
    sys.exit(0 if success else 1)