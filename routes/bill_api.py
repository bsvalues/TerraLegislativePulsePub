"""
Bill Tracking API Routes

This module contains the API routes for the bill tracking functionality
of the Benton County Assessor platform, allowing access to legislative bill data
and AI-powered analysis of their impact on property assessments.
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import AuditLog, db
from services.bill_analysis_service import (
    analyze_bill_impact, 
    analyze_tracked_bill,
    summarize_bill,
    extract_entities,
    search_relevant_bills
)
from services.trackers import get_all_tracked_bills, search_bills, get_bill_by_id

logger = logging.getLogger(__name__)

bill_api_bp = Blueprint('bill_api', __name__, url_prefix='/bills')

@bill_api_bp.route('/tracked', methods=['GET'])
@login_required
def get_tracked_bills():
    """
    Get all tracked bills across all sources.
    
    GET /bills/tracked
    
    Parameters:
    - source (str, optional): Filter by source
    - limit (int, optional): Limit the number of results
    """
    try:
        # Get query parameters
        source = request.args.get('source')
        limit = request.args.get('limit', 100, type=int)
        
        # Get all tracked bills
        all_bills = get_all_tracked_bills()
        
        # Filter by source if specified
        if source:
            all_bills = [bill for bill in all_bills if bill.get('source') == source]
        
        # Apply limit
        all_bills = all_bills[:limit]
        
        # Log the action
        _log_action('get_tracked_bills', 
                   f"Retrieved {len(all_bills)} tracked bills" + (f" from {source}" if source else ""))
        
        return jsonify({
            "bills": all_bills,
            "count": len(all_bills),
            "success": True
        })
        
    except Exception as e:
        logger.exception(f"Error retrieving tracked bills: {str(e)}")
        return jsonify({
            "error": f"Error retrieving tracked bills: {str(e)}"
        }), 500

@bill_api_bp.route('/search', methods=['GET'])
@login_required
def search_tracked_bills():
    """
    Search for bills across all trackers.
    
    GET /bills/search
    
    Parameters:
    - query (str): The search query
    - limit (int, optional): Limit the number of results
    """
    try:
        # Get query parameters
        query = request.args.get('query')
        limit = request.args.get('limit', 50, type=int)
        
        if not query:
            return jsonify({"error": "No search query provided"}), 400
        
        # Search for bills
        results = search_bills(query)
        
        # Apply limit
        results = results[:limit]
        
        # Log the action
        _log_action('search_bills', 
                   f"Searched bills with query '{query}', found {len(results)} results")
        
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results),
            "success": True
        })
        
    except Exception as e:
        logger.exception(f"Error searching bills: {str(e)}")
        return jsonify({
            "error": f"Error searching bills: {str(e)}"
        }), 500

@bill_api_bp.route('/analyze/<bill_id>', methods=['GET'])
@login_required
def analyze_tracked_bill_endpoint(bill_id):
    """
    Analyze a tracked bill by its ID.
    
    GET /bills/analyze/<bill_id>
    
    Parameters:
    - source (str, optional): The source tracker
    - property_class (str, optional): Property class to focus on
    - property_value (float, optional): Property value to consider
    """
    try:
        # Get query parameters
        source = request.args.get('source')
        property_class = request.args.get('property_class')
        property_value = request.args.get('property_value', type=float)
        
        # Analyze the bill
        analysis = analyze_tracked_bill(
            bill_id=bill_id,
            source=source,
            property_class=property_class,
            property_value=property_value
        )
        
        if not analysis.get('success', False):
            return jsonify(analysis), 404
        
        # Log the action
        _log_action('analyze_tracked_bill', 
                   f"Analyzed tracked bill {bill_id}" + (f" from {source}" if source else ""))
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.exception(f"Error analyzing tracked bill: {str(e)}")
        return jsonify({
            "error": f"Error analyzing tracked bill: {str(e)}"
        }), 500

@bill_api_bp.route('/relevant', methods=['GET'])
@login_required
def find_relevant_bills():
    """
    Find bills relevant to a search query.
    
    GET /bills/relevant
    
    Parameters:
    - query (str): The search query
    - limit (int, optional): Maximum number of results per source
    """
    try:
        # Get query parameters
        query = request.args.get('query')
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({"error": "No search query provided"}), 400
        
        # Search for relevant bills
        results = search_relevant_bills(query, limit)
        
        # Log the action
        _log_action('find_relevant_bills', 
                   f"Found bills relevant to '{query}'")
        
        return jsonify(results)
        
    except Exception as e:
        logger.exception(f"Error finding relevant bills: {str(e)}")
        return jsonify({
            "error": f"Error finding relevant bills: {str(e)}"
        }), 500

@bill_api_bp.route('/summarize/<bill_id>', methods=['GET'])
@login_required
def summarize_tracked_bill(bill_id):
    """
    Generate a summary of a tracked bill.
    
    GET /bills/summarize/<bill_id>
    
    Parameters:
    - source (str, optional): The source tracker
    - summary_type (str, optional): Type of summary (general, technical, public)
    - length (str, optional): Length of summary (short, medium, long)
    """
    try:
        # Get query parameters
        source = request.args.get('source')
        summary_type = request.args.get('summary_type', 'general')
        length = request.args.get('length', 'medium')
        
        # Validate enum values
        valid_summary_types = ['general', 'technical', 'public']
        valid_lengths = ['short', 'medium', 'long']
        
        if summary_type not in valid_summary_types:
            return jsonify({"error": f"Invalid summary_type. Must be one of: {', '.join(valid_summary_types)}"}), 400
            
        if length not in valid_lengths:
            return jsonify({"error": f"Invalid length. Must be one of: {', '.join(valid_lengths)}"}), 400
        
        # Get the bill
        bill = get_bill_by_id(bill_id, source)
        
        if not bill:
            return jsonify({
                "error": f"Bill {bill_id} not found",
                "success": False
            }), 404
        
        # Get the text content
        bill_text = bill.get("summary", "")
        if not bill_text or len(bill_text) < 100:
            bill_text = f"Bill {bill_id}: {bill.get('title', '')}\n\n{bill.get('description', '')}"
        
        # Generate the summary
        summary_result = summarize_bill(
            bill_text=bill_text,
            bill_title=bill.get("title", f"Bill {bill_id}"),
            summary_type=summary_type,
            length=length
        )
        
        # Add bill metadata
        summary_result["bill_id"] = bill_id
        summary_result["bill_title"] = bill.get("title", "")
        summary_result["bill_source"] = bill.get("source", source or "unknown")
        
        # Log the action
        _log_action('summarize_tracked_bill', 
                   f"Summarized tracked bill {bill_id} ({summary_type}, {length})")
        
        return jsonify(summary_result)
        
    except Exception as e:
        logger.exception(f"Error summarizing tracked bill: {str(e)}")
        return jsonify({
            "error": f"Error summarizing tracked bill: {str(e)}"
        }), 500

@bill_api_bp.route('/extract-entities/<bill_id>', methods=['GET'])
@login_required
def extract_entities_from_bill(bill_id):
    """
    Extract entities from a tracked bill.
    
    GET /bills/extract-entities/<bill_id>
    
    Parameters:
    - source (str, optional): The source tracker
    - entity_types (str, optional): Comma-separated list of entity types to extract
    """
    try:
        # Get query parameters
        source = request.args.get('source')
        entity_types_param = request.args.get('entity_types', '')
        
        # Parse entity types
        entity_types = [t.strip() for t in entity_types_param.split(',')] if entity_types_param else [
            'organization', 'person', 'location', 'date', 'money'
        ]
        
        # Get the bill
        bill = get_bill_by_id(bill_id, source)
        
        if not bill:
            return jsonify({
                "error": f"Bill {bill_id} not found",
                "success": False
            }), 404
        
        # Get the text content
        bill_text = bill.get("summary", "")
        if not bill_text or len(bill_text) < 100:
            bill_text = f"Bill {bill_id}: {bill.get('title', '')}\n\n{bill.get('description', '')}"
        
        # Extract entities
        extraction_result = extract_entities(
            bill_text=bill_text,
            bill_title=bill.get("title", f"Bill {bill_id}"),
            entity_types=entity_types
        )
        
        # Add bill metadata
        extraction_result["bill_id"] = bill_id
        extraction_result["bill_title"] = bill.get("title", "")
        extraction_result["bill_source"] = bill.get("source", source or "unknown")
        
        # Log the action
        _log_action('extract_entities_from_bill', 
                   f"Extracted entities from tracked bill {bill_id}")
        
        return jsonify(extraction_result)
        
    except Exception as e:
        logger.exception(f"Error extracting entities from bill: {str(e)}")
        return jsonify({
            "error": f"Error extracting entities from bill: {str(e)}"
        }), 500

def _log_action(action, details):
    """Log an action to the audit log"""
    try:
        if current_user and current_user.is_authenticated:
            log_entry = AuditLog(
                user_id=current_user.id,
                action=f"bill_api.{action}",
                details=details,
                entity_type="bill_tracking",
                ip_address=request.remote_addr
            )
            db.session.add(log_entry)
            db.session.commit()
    except Exception as e:
        logger.error(f"Error logging action: {str(e)}")
        # Don't raise the exception - logging shouldn't block API responses