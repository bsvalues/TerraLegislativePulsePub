"""
API Routes

This module contains general API routes for the Benton County Assessor platform.
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, AuditLog

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/test-api-key', methods=['POST'])
@login_required
def test_api_key():
    """
    Test an API key for a specific service
    
    POST /api/test-api-key
    
    Request Body:
    - service: The service name (anthropic, legiscan, openstates)
    - api_key: The API key to test
    """
    try:
        data = request.json
        
        # Check required fields
        required_fields = ['service', 'api_key']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}", "success": False}), 400
        
        service = data['service']
        api_key = data['api_key']
        
        # Import the API key manager
        from utils.api_key_manager import ApiKeyManager
        
        # Test the API key for the specified service
        if service == 'anthropic':
            success = ApiKeyManager.test_anthropic_key(api_key)
        elif service == 'legiscan':
            success = ApiKeyManager.test_legiscan_key(api_key)
        elif service == 'openstates':
            success = ApiKeyManager.test_openstates_key(api_key)
        else:
            return jsonify({"error": f"Unknown service: {service}", "success": False}), 400
        
        if success:
            # Log the action
            _log_action(f"test_{service}_api_key", "API key test successful")
            return jsonify({"success": True})
        else:
            return jsonify({"error": "API key test failed", "success": False})
        
    except Exception as e:
        logger.exception(f"Error testing API key: {str(e)}")
        return jsonify({"error": f"Error testing API key: {str(e)}", "success": False}), 500

@api_bp.route('/run-tracker', methods=['POST'])
@login_required
def run_tracker():
    """
    Run a specific legislative tracker update
    
    POST /api/run-tracker
    
    Request Body:
    - tracker: The tracker name (wa_legislature, openstates, legiscan, local_docs, all)
    """
    try:
        data = request.json
        
        # Check required fields
        if 'tracker' not in data:
            return jsonify({"error": "Missing required field: tracker", "success": False}), 400
        
        tracker = data['tracker']
        updated_count = 0
        
        # Run the specified tracker
        if tracker == 'wa_legislature':
            from services.trackers.wa_legislature import fetch_and_store
            updated_count = fetch_and_store()
        elif tracker == 'openstates':
            from services.trackers.openstates import update_all_bills
            updated_count = update_all_bills()
        elif tracker == 'legiscan':
            from services.trackers.legiscan import update_all_bills
            updated_count = update_all_bills()
        elif tracker == 'local_docs':
            from services.trackers.local_docs import update_all_documents
            updated_count = update_all_documents()
        elif tracker == 'all':
            # Run all trackers
            from scheduler import update_all_trackers
            update_all_trackers()
            updated_count = -1  # Special value for "all"
        else:
            return jsonify({"error": f"Unknown tracker: {tracker}", "success": False}), 400
        
        # Log the action
        _log_action(f"run_{tracker}_tracker", f"Updated {updated_count} items")
        
        return jsonify({
            "success": True, 
            "updated_count": updated_count,
            "message": f"Tracker {tracker} updated successfully"
        })
        
    except Exception as e:
        logger.exception(f"Error running tracker: {str(e)}")
        return jsonify({"error": f"Error running tracker: {str(e)}", "success": False}), 500

def _log_action(action, details):
    """Log an action to the audit log"""
    try:
        if current_user and current_user.is_authenticated:
            log_entry = AuditLog(
                user_id=current_user.id,
                action=f"api.{action}",
                details=details,
                entity_type="api",
                ip_address=request.remote_addr
            )
            db.session.add(log_entry)
            db.session.commit()
    except Exception as e:
        logger.error(f"Error logging action: {str(e)}")
        # Don't raise the exception - logging shouldn't block API responses