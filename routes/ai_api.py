"""
AI API Routes

This module contains the routes for the AI-powered analysis API endpoints.
"""

import logging
from typing import Dict, Any, List, Union, Tuple
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required

from services.bill_analysis_service import (
    analyze_tracked_bill,
    categorize_bill,
    batch_analyze_bills
)
from services.bill_search_service import get_bill_by_id

logger = logging.getLogger(__name__)

ai_api_bp = Blueprint('ai_api', __name__, url_prefix='/api/ai')

@ai_api_bp.route('/analyze/<bill_id>', methods=['GET'])
@login_required
def analyze_bill(bill_id):
    """
    Analyze a bill using AI
    
    Query parameters:
    - analysis_type: Type of analysis (summary, entities, impact)
    - source: Source of the bill (optional)
    """
    analysis_type = request.args.get('analysis_type', 'impact')
    source = request.args.get('source', None)
    
    # Validate analysis type
    valid_types = ['summary', 'entities', 'impact']
    if analysis_type not in valid_types:
        return jsonify({
            'error': f"Invalid analysis type. Must be one of: {', '.join(valid_types)}"
        }), 400
    
    # Analyze the bill
    try:
        result = analyze_tracked_bill(bill_id, analysis_type, source)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify(result)
    except Exception as e:
        logger.exception(f"Error analyzing bill {bill_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_api_bp.route('/categorize/<bill_id>', methods=['GET'])
@login_required
def categorize_bill_route(bill_id):
    """
    Categorize a bill by property class and impact level
    
    Query parameters:
    - source: Source of the bill (optional)
    """
    source = request.args.get('source', None)
    
    # Categorize the bill
    try:
        result = categorize_bill(bill_id, source)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify(result)
    except Exception as e:
        logger.exception(f"Error categorizing bill {bill_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_api_bp.route('/batch-analyze', methods=['POST'])
@login_required
def batch_analyze():
    """
    Analyze multiple bills in batch
    
    JSON body:
    - bill_ids: List of bill IDs to analyze
    - analysis_type: Type of analysis (summary, entities, impact)
    """
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate input
    bill_ids = data.get('bill_ids', [])
    analysis_type = data.get('analysis_type', 'impact')
    
    if not bill_ids or not isinstance(bill_ids, list):
        return jsonify({'error': 'bill_ids must be a non-empty list'}), 400
    
    # Validate analysis type
    valid_types = ['summary', 'entities', 'impact']
    if analysis_type not in valid_types:
        return jsonify({
            'error': f"Invalid analysis type. Must be one of: {', '.join(valid_types)}"
        }), 400
    
    # Process batch
    try:
        result = batch_analyze_bills(bill_ids, analysis_type)
        return jsonify(result)
    except Exception as e:
        logger.exception(f"Error in batch analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500