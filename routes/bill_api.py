"""
Bill API Routes

This module contains API routes for interacting with legislative bills.
"""

import logging
from typing import Dict, Any, List, Optional

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from services.bill_search_service import get_all_tracked_bills, search_bills, get_bill_by_id, search_relevant_bills
from services.bill_analysis_service import analyze_tracked_bill, categorize_bill
from models import LegislativeUpdate, db

logger = logging.getLogger(__name__)

bill_api_bp = Blueprint('bill_api', __name__, url_prefix='/bills')

@bill_api_bp.route('/tracked', methods=['GET'])
@login_required
def get_tracked_bills():
    """
    Get all tracked bills
    
    GET /api/bills/tracked
    
    Query Parameters:
    - limit: Maximum number of bills to return (default: 100)
    - source: Filter by source (optional)
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        source = request.args.get('source')
        
        bills = get_all_tracked_bills(limit=limit, source=source)
        
        return jsonify({
            "success": True,
            "count": len(bills),
            "bills": bills
        })
        
    except Exception as e:
        logger.exception(f"Error getting tracked bills: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bill_api_bp.route('/search', methods=['GET'])
@login_required
def search_bill_api():
    """
    Search for bills
    
    GET /api/bills/search
    
    Query Parameters:
    - query: The search query
    - source: Filter by source (optional)
    """
    try:
        query = request.args.get('query', '')
        source = request.args.get('source')
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Missing required parameter: query"
            }), 400
        
        bills = search_bills(query, source=source)
        
        return jsonify({
            "success": True,
            "count": len(bills),
            "query": query,
            "bills": bills
        })
        
    except Exception as e:
        logger.exception(f"Error searching bills: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bill_api_bp.route('/relevant', methods=['GET'])
@login_required
def find_relevant_bills():
    """
    Find bills relevant to a natural language question
    
    GET /api/bills/relevant
    
    Query Parameters:
    - question: The natural language question
    """
    try:
        question = request.args.get('question', '')
        
        if not question:
            return jsonify({
                "success": False,
                "error": "Missing required parameter: question"
            }), 400
        
        bills = search_relevant_bills(question)
        
        return jsonify({
            "success": True,
            "count": len(bills),
            "question": question,
            "bills": bills
        })
        
    except Exception as e:
        logger.exception(f"Error finding relevant bills: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bill_api_bp.route('/<bill_id>', methods=['GET'])
@login_required
def get_bill(bill_id):
    """
    Get a specific bill
    
    GET /api/bills/<bill_id>
    
    Query Parameters:
    - source: The source of the bill (optional)
    """
    try:
        source = request.args.get('source')
        
        bill = get_bill_by_id(bill_id, source=source)
        
        if not bill:
            return jsonify({
                "success": False,
                "error": f"Bill {bill_id} not found"
            }), 404
        
        return jsonify({
            "success": True,
            "bill": bill
        })
        
    except Exception as e:
        logger.exception(f"Error getting bill {bill_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bill_api_bp.route('/<bill_id>/analyze', methods=['GET'])
@login_required
def analyze_bill(bill_id):
    """
    Analyze a bill
    
    GET /api/bills/<bill_id>/analyze
    
    Query Parameters:
    - analysis_type: Type of analysis to perform (impact, summary, entities)
    - property_class: Specific property class to analyze for (optional)
    - source: The source of the bill (optional)
    """
    try:
        analysis_type = request.args.get('analysis_type', 'impact')
        property_class = request.args.get('property_class')
        source = request.args.get('source')
        
        analysis = analyze_tracked_bill(
            bill_id=bill_id,
            analysis_type=analysis_type,
            property_class=property_class,
            source=source
        )
        
        return jsonify({
            "success": True,
            "bill_id": bill_id,
            "analysis_type": analysis_type,
            "analysis": analysis
        })
        
    except Exception as e:
        logger.exception(f"Error analyzing bill {bill_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500