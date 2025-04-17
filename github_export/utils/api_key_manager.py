"""
API Key Manager

This module provides utilities for managing and validating API keys for external services.
"""

import os
import logging
from flask import current_app, flash, session
import requests

logger = logging.getLogger(__name__)

class ApiKeyManager:
    """
    Manager for API keys used by the application.
    
    Provides functionality to check key status, validate keys with test requests,
    and manage key storage.
    """
    
    @staticmethod
    def check_api_key_status():
        """
        Check the status of all configured API keys.
        
        Returns:
            dict: Status of each API service
        """
        status = {
            'anthropic': {
                'configured': bool(current_app.config.get('ANTHROPIC_API_KEY')),
                'status': 'unknown'
            },
            'legiscan': {
                'configured': bool(current_app.config.get('LEGISCAN_API_KEY')),
                'status': 'unknown'
            },
            'openstates': {
                'configured': bool(current_app.config.get('OPENSTATES_API_KEY')),
                'status': 'unknown'
            }
        }
        
        # Check Anthropic key
        if status['anthropic']['configured']:
            try:
                from services.anthropic_service import get_anthropic_client
                client = get_anthropic_client()
                if client:
                    status['anthropic']['status'] = 'valid'
                else:
                    status['anthropic']['status'] = 'invalid'
            except Exception as e:
                logger.error(f"Error checking Anthropic API key: {str(e)}")
                status['anthropic']['status'] = 'error'
        
        # Check LegiScan key (basic check - doesn't validate with API)
        if status['legiscan']['configured']:
            try:
                key = current_app.config.get('LEGISCAN_API_KEY')
                if key and len(key) > 10:  # Simple length check
                    status['legiscan']['status'] = 'configured'
            except Exception as e:
                logger.error(f"Error checking LegiScan API key: {str(e)}")
                status['legiscan']['status'] = 'error'
        
        # Check OpenStates key (basic check - doesn't validate with API)
        if status['openstates']['configured']:
            try:
                key = current_app.config.get('OPENSTATES_API_KEY')
                if key and len(key) > 10:  # Simple length check
                    status['openstates']['status'] = 'configured'
            except Exception as e:
                logger.error(f"Error checking OpenStates API key: {str(e)}")
                status['openstates']['status'] = 'error'
        
        return status
    
    @staticmethod
    def test_anthropic_key(key):
        """
        Test if an Anthropic API key is valid
        
        Args:
            key (str): The API key to test
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            import anthropic
            from anthropic import Anthropic
            
            client = Anthropic(api_key=key)
            
            # Simple test message
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                temperature=0,
                system="You are a helpful assistant.",
                messages=[
                    {"role": "user", "content": "Say hello"}
                ]
            )
            
            if message and message.content and len(message.content) > 0:
                return True
            return False
            
        except Exception as e:
            logger.error(f"Anthropic API key test failed: {str(e)}")
            return False
    
    @staticmethod
    def test_legiscan_key(key):
        """
        Test if a LegiScan API key is valid
        
        Args:
            key (str): The API key to test
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Simple API request to test the key
            url = "https://api.legiscan.com/"
            params = {
                "key": key,
                "op": "getMasterList",
                "state": "WA"
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "OK":
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"LegiScan API key test failed: {str(e)}")
            return False
    
    @staticmethod
    def test_openstates_key(key):
        """
        Test if an OpenStates API key is valid
        
        Args:
            key (str): The API key to test
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Simple API request to test the key
            url = "https://v3.openstates.org/bills"
            params = {
                "apikey": key,
                "jurisdiction": "Washington",
                "per_page": 1
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"OpenStates API key test failed: {str(e)}")
            return False

    @staticmethod
    def update_api_key(service, key, test=True):
        """
        Update an API key for a service
        
        Args:
            service (str): The service name (anthropic, legiscan, openstates)
            key (str): The new API key
            test (bool): Whether to test the key before saving
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Test the key if requested
        if test:
            if service == 'anthropic':
                if not ApiKeyManager.test_anthropic_key(key):
                    return False
            elif service == 'legiscan':
                if not ApiKeyManager.test_legiscan_key(key):
                    return False
            elif service == 'openstates':
                if not ApiKeyManager.test_openstates_key(key):
                    return False
            else:
                return False
        
        # Map service to config key
        config_key_map = {
            'anthropic': 'ANTHROPIC_API_KEY',
            'legiscan': 'LEGISCAN_API_KEY',
            'openstates': 'OPENSTATES_API_KEY'
        }
        
        if service not in config_key_map:
            return False
            
        # Update the config
        try:
            current_app.config[config_key_map[service]] = key
            # Store in environment for persistence
            os.environ[config_key_map[service]] = key
            
            # Note: In a production environment, we would use a more secure
            # method of storing API keys, such as a secure key management service
            
            return True
        except Exception as e:
            logger.error(f"Error updating {service} API key: {str(e)}")
            return False