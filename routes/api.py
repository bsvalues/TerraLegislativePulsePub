import logging
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from mcp.message_protocol import MCPMessage
from utils.validators import validate_request_data
from models import AuditLog, db

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/mcp/status', methods=['GET'])
@login_required
def get_mcp_status():
    """Get the current status of the MCP and agents"""
    try:
        mcp = current_app.config['MCP']
        status = mcp.get_status()
        
        # Log the action
        log_action('status_check', 'Checked MCP status')
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.exception(f"Error getting MCP status: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error getting MCP status: {str(e)}"
        }), 500

@api_bp.route('/mcp/property-validate', methods=['POST'])
@login_required
def validate_property():
    """Validate property data against WA standards"""
    try:
        # Validate request data
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        if 'property_data' not in data:
            return jsonify({
                'success': False,
                'error': 'No property_data provided'
            }), 400
        
        # Get the MCP instance
        mcp = current_app.config['MCP']
        
        # Process the request
        response = mcp.process_api_request('/api/mcp/property-validate', data)
        
        # Log the action
        property_id = data.get('property_data', {}).get('parcel_id', 'Unknown')
        log_action('property_validate', f"Validated property data for {property_id}")
        
        return jsonify(response)
    except Exception as e:
        logger.exception(f"Error validating property data: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error validating property data: {str(e)}"
        }), 500

@api_bp.route('/mcp/property-value', methods=['POST'])
@login_required
def value_property():
    """Calculate property value using specified approach"""
    try:
        # Validate request data
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        if 'property_data' not in data:
            return jsonify({
                'success': False,
                'error': 'No property_data provided'
            }), 400
        
        # Get the MCP instance
        mcp = current_app.config['MCP']
        
        # Process the request
        response = mcp.process_api_request('/api/mcp/property-value', data)
        
        # Log the action
        property_id = data.get('property_data', {}).get('parcel_id', 'Unknown')
        approach = data.get('valuation_approach', 'market')
        log_action('property_value', f"Calculated {approach} value for property {property_id}")
        
        return jsonify(response)
    except Exception as e:
        logger.exception(f"Error calculating property value: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error calculating property value: {str(e)}"
        }), 500

@api_bp.route('/mcp/property-impact', methods=['POST'])
@login_required
def analyze_impact():
    """Analyze how legislation impacts property assessments"""
    try:
        # Validate request data
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Get the MCP instance
        mcp = current_app.config['MCP']
        
        # Process the request
        response = mcp.process_api_request('/api/mcp/property-impact', data)
        
        # Log the action
        analysis_type = data.get('analysis_type', 'bill')
        target = data.get('bill_id', data.get('property_class', 'Unknown'))
        log_action('property_impact', f"Analyzed {analysis_type} impact for {target}")
        
        return jsonify(response)
    except Exception as e:
        logger.exception(f"Error analyzing legislative impact: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error analyzing legislative impact: {str(e)}"
        }), 500

@api_bp.route('/mcp/user-query', methods=['POST'])
@login_required
def process_user_query():
    """Process natural language queries from staff"""
    try:
        # Validate request data
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        if 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'No query provided'
            }), 400
        
        # Get the MCP instance
        mcp = current_app.config['MCP']
        
        # Process the request
        response = mcp.process_api_request('/api/mcp/user-query', data)
        
        # Log the action
        query = data.get('query', 'Unknown')
        log_action('user_query', f"Processed user query: {query[:50]}...")
        
        return jsonify(response)
    except Exception as e:
        logger.exception(f"Error processing user query: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error processing user query: {str(e)}"
        }), 500

@api_bp.route('/mcp/batch-validate', methods=['POST'])
@login_required
def batch_validate():
    """Validate multiple properties in a batch"""
    try:
        # Validate request data
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        if 'properties' not in data:
            return jsonify({
                'success': False,
                'error': 'No properties provided'
            }), 400
        
        # Get the MCP instance
        mcp = current_app.config['MCP']
        
        # Process the request
        response = mcp.process_api_request('/api/mcp/batch-validate', data)
        
        # Log the action
        count = len(data.get('properties', []))
        log_action('batch_validate', f"Batch validated {count} properties")
        
        return jsonify(response)
    except Exception as e:
        logger.exception(f"Error in batch validation: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error in batch validation: {str(e)}"
        }), 500

def log_action(action, details):
    """Log an action to the audit log"""
    try:
        if current_user.is_authenticated:
            # Create a new audit log entry
            log_entry = AuditLog(
                user_id=current_user.id,
                action=action,
                details=details,
                ip_address=request.remote_addr
            )
            
            # Add and commit to the database
            db.session.add(log_entry)
            db.session.commit()
    except Exception as e:
        logger.exception(f"Error logging action: {str(e)}")
        # Continue without failing if logging fails
