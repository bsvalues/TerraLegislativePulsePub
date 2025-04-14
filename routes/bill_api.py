"""
Bill API Routes

This module contains the routes for the bill API endpoints.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required

from models import LegislativeUpdate, db
from services.bill_search_service import (
    get_all_tracked_bills,
    search_bills,
    get_bill_by_id,
    search_relevant_bills,
    get_recent_bills,
    get_high_impact_bills
)

logger = logging.getLogger(__name__)

bill_api_bp = Blueprint('bill_api', __name__, url_prefix='/api/bills')

@bill_api_bp.route('/', methods=['GET'])
@login_required
def get_bills():
    """
    Get all tracked bills with optional filtering
    
    Query parameters:
    - limit: Maximum number of bills to return (default: 50)
    - offset: Offset for pagination (default: 0)
    - source: Filter by source (optional)
    """
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    source = request.args.get('source', None)
    
    try:
        bills = get_all_tracked_bills(limit, offset, source)
        return jsonify(bills)
    except Exception as e:
        logger.exception(f"Error getting bills: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bill_api_bp.route('/search', methods=['GET'])
@login_required
def search_bills_route():
    """
    Search for bills
    
    Query parameters:
    - q: Search term
    - sources: Comma-separated list of sources to search
    - limit: Maximum number of bills to return (default: 50)
    - offset: Offset for pagination (default: 0)
    """
    search_term = request.args.get('q', '')
    sources_str = request.args.get('sources', '')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    if not search_term:
        return jsonify({'error': 'Search term is required'}), 400
    
    sources = sources_str.split(',') if sources_str else None
    
    try:
        bills = search_bills(search_term, sources, limit, offset)
        return jsonify(bills)
    except Exception as e:
        logger.exception(f"Error searching bills: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bill_api_bp.route('/<bill_id>', methods=['GET'])
@login_required
def get_bill(bill_id):
    """
    Get a specific bill by ID
    
    Query parameters:
    - source: Source of the bill (optional)
    """
    source = request.args.get('source', None)
    
    try:
        bill = get_bill_by_id(bill_id, source)
        
        if not bill:
            return jsonify({'error': f'Bill {bill_id} not found'}), 404
        
        return jsonify(bill)
    except Exception as e:
        logger.exception(f"Error getting bill {bill_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bill_api_bp.route('/relevant', methods=['GET'])
@login_required
def get_relevant_bills():
    """
    Get bills relevant to a specific property class
    
    Query parameters:
    - property_class: The property class (e.g., 'Residential')
    - keywords: Comma-separated list of keywords to further filter results
    - limit: Maximum number of bills to return (default: 50)
    """
    property_class = request.args.get('property_class', '')
    keywords_str = request.args.get('keywords', '')
    limit = request.args.get('limit', 50, type=int)
    
    if not property_class:
        return jsonify({'error': 'Property class is required'}), 400
    
    keywords = keywords_str.split(',') if keywords_str else None
    
    try:
        bills = search_relevant_bills(property_class, keywords, limit)
        return jsonify(bills)
    except Exception as e:
        logger.exception(f"Error getting relevant bills: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bill_api_bp.route('/recent', methods=['GET'])
@login_required
def get_recent_bills_route():
    """
    Get bills updated in the last N days
    
    Query parameters:
    - days: Number of days to look back (default: 30)
    - limit: Maximum number of bills to return (default: 10)
    """
    days = request.args.get('days', 30, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    try:
        bills = get_recent_bills(days, limit)
        return jsonify(bills)
    except Exception as e:
        logger.exception(f"Error getting recent bills: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bill_api_bp.route('/high-impact', methods=['GET'])
@login_required
def get_high_impact_bills_route():
    """
    Get bills with high impact
    
    Query parameters:
    - limit: Maximum number of bills to return (default: 10)
    """
    limit = request.args.get('limit', 10, type=int)
    
    try:
        bills = get_high_impact_bills(limit)
        return jsonify(bills)
    except Exception as e:
        logger.exception(f"Error getting high impact bills: {str(e)}")
        return jsonify({'error': str(e)}), 500