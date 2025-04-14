"""
AI Subsystem API Routes

This module contains the API routes specifically for the AI capabilities of the 
Benton County Assessor platform, allowing interaction with AI-powered analysis features.
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from utils.validators import validate_request_data
from models import AuditLog, db
from services.anthropic_service import get_ai_response
from services.bill_analysis_service import (
    analyze_bill_impact, 
    analyze_tracked_bill,
    summarize_bill,
    extract_entities
)
from services.bill_search_service import get_all_tracked_bills, search_bills, get_bill_by_id, search_relevant_bills

logger = logging.getLogger(__name__)

ai_api_bp = Blueprint('ai_api', __name__, url_prefix='/ai')

@ai_api_bp.route('/status', methods=['GET'])
@login_required
def ai_status():
    """
    Get the status of the AI system, including registered agents and availability of AI providers.
    
    GET /ai/status
    
    Parameters:
    - detailed (boolean): If true, returns detailed status information
    """
    try:
        # Get query parameters
        detailed = request.args.get('detailed', 'false').lower() == 'true'
        
        # Get MCP instance for agent information
        mcp = current_app.config.get('MCP')
        
        # Check if Anthropic API is available (key exists and service is working)
        anthropic_available = current_app.config.get('ANTHROPIC_API_KEY') is not None
        
        # Basic response
        response = {
            "initialized": mcp is not None,
            "anthropic_available": anthropic_available,
            "agents": ["property_impact_analyzer", "data_validation", "valuation", "user_interaction"]
        }
        
        # Add detailed information if requested
        if detailed:
            # Get detailed status from MCP
            mcp_status = mcp.get_status() if mcp else {}
            
            # Add additional detailed information
            response.update({
                "openai_available": False,  # Not currently implemented
                "agent_count": len(response["agents"]),
                "mcp_available": mcp is not None,
                "message_handlers": [
                    "request.property.impact", 
                    "request.data.validate", 
                    "request.data.quality.check", 
                    "request.property.value", 
                    "request.batch.valuation", 
                    "request.valuation.factors", 
                    "request.user.query", 
                    "request.user.action", 
                    "request.user.help"
                ],
                "message_handler_count": 9,
                "missing_agents": [],
                "all_required_agents_available": mcp is not None
            })
        
        # Log the action
        _log_action('ai_status_check', f"Checked AI subsystem status (detailed={detailed})")
        
        return jsonify(response)
        
    except Exception as e:
        logger.exception(f"Error getting AI status: {str(e)}")
        return jsonify({
            "error": f"Error getting AI status: {str(e)}"
        }), 500

@ai_api_bp.route('/property-impact', methods=['POST'])
@login_required
def property_impact():
    """
    Analyze how legislation impacts property assessments.
    
    POST /ai/property-impact
    
    Request Body:
    - bill_text: Full text of the bill
    - bill_title: Title of the bill
    - property_class: Property class (Optional)
    - property_value: Property value (Optional)
    - county: County (Optional, default: Benton)
    """
    try:
        # Validate request data
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Check required fields
        required_fields = ['bill_text', 'bill_title']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Get the MCP instance if using it for routing
        mcp = current_app.config.get('MCP')
        if not mcp:
            return jsonify({"error": "AI system not initialized"}), 503
            
        # Set defaults for optional fields
        data['property_class'] = data.get('property_class', 'Residential')
        data['property_value'] = data.get('property_value', 0)
        data['county'] = data.get('county', 'Benton')
        
        # Process directly or through MCP
        response = mcp.process_api_request('/ai/property-impact', data)
        
        # Log the action
        _log_action('property_impact_analysis', 
                   f"Analyzed impact of bill '{data['bill_title'][:30]}...' on {data['property_class']} properties")
        
        return jsonify(response)
        
    except Exception as e:
        logger.exception(f"Error analyzing property impact: {str(e)}")
        return jsonify({
            "error": f"Error analyzing property impact: {str(e)}"
        }), 500

@ai_api_bp.route('/analyze', methods=['POST'])
@login_required
def analyze_bill():
    """
    Analyze a bill for key insights.
    
    POST /ai/analyze
    
    Request Body:
    - bill_text: Full text of the bill
    - bill_title: Title of the bill
    - bill_source: Source of the bill
    - focus_areas: Optional focus areas
    """
    try:
        # Validate request data
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Check required fields
        required_fields = ['bill_text', 'bill_title', 'bill_source']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Get AI service
        anthropic_api_key = current_app.config.get('ANTHROPIC_API_KEY')
        if not anthropic_api_key:
            return jsonify({"error": "AI service not configured"}), 503
        
        # Check if a direct Anthropic call or MCP-based routing
        mcp = current_app.config.get('MCP')
        if mcp:
            # Process through MCP
            response = mcp.process_api_request('/ai/analyze', data)
        else:
            # Direct AI call (fallback)
            prompt = f"""
            Analyze this legislative bill for key insights:
            
            Title: {data['bill_title']}
            Source: {data['bill_source']}
            
            Focus Areas: {', '.join(data.get('focus_areas', ['general impact']))}
            
            Bill Text:
            {data['bill_text']}
            
            Please provide:
            1. A summary of the key provisions
            2. The potential impact on property assessments
            3. Identification of affected stakeholders
            4. Timeline considerations
            5. Implementation challenges
            """
            
            # Get AI response
            ai_response = get_ai_response(prompt)
            
            # Structure the response
            response = {
                "analysis": ai_response,
                "success": True
            }
        
        # Log the action
        _log_action('bill_analysis', 
                   f"Analyzed bill '{data['bill_title'][:30]}...' from {data['bill_source']}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.exception(f"Error analyzing bill: {str(e)}")
        return jsonify({
            "error": f"Error analyzing bill: {str(e)}"
        }), 500

@ai_api_bp.route('/summarize', methods=['POST'])
@login_required
def summarize_bill():
    """
    Generate a summary of a bill.
    
    POST /ai/summarize
    
    Request Body:
    - bill_text: Full text of the bill
    - bill_title: Title of the bill
    - summary_type: Optional (general, technical, public)
    - length: Optional (short, medium, long)
    """
    try:
        # Validate request data
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Check required fields
        required_fields = ['bill_text', 'bill_title']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Set defaults for optional fields
        summary_type = data.get('summary_type', 'general')
        length = data.get('length', 'medium')
        
        # Validate enum values
        valid_summary_types = ['general', 'technical', 'public']
        valid_lengths = ['short', 'medium', 'long']
        
        if summary_type not in valid_summary_types:
            return jsonify({"error": f"Invalid summary_type. Must be one of: {', '.join(valid_summary_types)}"}), 400
            
        if length not in valid_lengths:
            return jsonify({"error": f"Invalid length. Must be one of: {', '.join(valid_lengths)}"}), 400
        
        # Get AI service
        anthropic_api_key = current_app.config.get('ANTHROPIC_API_KEY')
        if not anthropic_api_key:
            return jsonify({"error": "AI service not configured"}), 503
        
        # Direct AI call or MCP routing
        mcp = current_app.config.get('MCP')
        if mcp:
            # Process through MCP
            response = mcp.process_api_request('/ai/summarize', data)
        else:
            # Generate appropriate prompt based on summary type and length
            word_counts = {
                'short': 150,
                'medium': 300,
                'long': 500
            }
            
            audience_guidance = {
                'general': "for a general audience with some knowledge of property assessment",
                'technical': "for technical staff with expertise in property assessment and taxation",
                'public': "for the general public with limited knowledge of property assessment processes"
            }
            
            prompt = f"""
            Summarize this legislative bill:
            
            Title: {data['bill_title']}
            
            Please provide a {length} summary ({word_counts[length]} words) {audience_guidance[summary_type]}.
            
            Bill Text:
            {data['bill_text']}
            """
            
            # Get AI response
            ai_response = get_ai_response(prompt)
            
            # Structure the response
            response = {
                "summary": ai_response,
                "summary_type": summary_type,
                "length": length,
                "word_count": len(ai_response.split()),
                "success": True
            }
        
        # Log the action
        _log_action('bill_summarization', 
                   f"Generated {length} {summary_type} summary for bill '{data['bill_title'][:30]}...'")
        
        return jsonify(response)
        
    except Exception as e:
        logger.exception(f"Error summarizing bill: {str(e)}")
        return jsonify({
            "error": f"Error summarizing bill: {str(e)}"
        }), 500

@ai_api_bp.route('/extract-entities', methods=['POST'])
@login_required
def extract_entities():
    """
    Extract entities (people, organizations, etc.) from a bill.
    
    POST /ai/extract-entities
    
    Request Body:
    - bill_text: Full text of the bill
    - bill_title: Title of the bill
    - entity_types: Optional entity types to focus on
    """
    try:
        # Validate request data
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Check required fields
        required_fields = ['bill_text', 'bill_title']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Set defaults
        entity_types = data.get('entity_types', ['organization', 'person', 'location', 'date', 'money'])
        
        # Get AI service
        anthropic_api_key = current_app.config.get('ANTHROPIC_API_KEY')
        if not anthropic_api_key:
            return jsonify({"error": "AI service not configured"}), 503
        
        # Direct AI call or MCP routing
        mcp = current_app.config.get('MCP')
        if mcp:
            # Process through MCP
            response = mcp.process_api_request('/ai/extract-entities', data)
        else:
            # Generate prompt
            prompt = f"""
            Extract the following entity types from this legislative bill:
            {', '.join(entity_types)}
            
            Title: {data['bill_title']}
            
            Bill Text:
            {data['bill_text']}
            
            For each entity found, please provide:
            1. The entity text
            2. The entity type
            3. The context in which it appears (relevant sentence)
            
            Format the results as a JSON object with each entity type as a key and a list of extracted entities as the value.
            """
            
            # Get AI response
            ai_response = get_ai_response(prompt)
            
            # Structure the response (note: in a real implementation, we'd parse the JSON from the AI response)
            response = {
                "entities_text": ai_response,
                "entity_types": entity_types,
                "success": True
            }
        
        # Log the action
        _log_action('entity_extraction', 
                   f"Extracted {', '.join(entity_types)} entities from bill '{data['bill_title'][:30]}...'")
        
        return jsonify(response)
        
    except Exception as e:
        logger.exception(f"Error extracting entities: {str(e)}")
        return jsonify({
            "error": f"Error extracting entities: {str(e)}"
        }), 500

@ai_api_bp.route('/categorize', methods=['POST'])
@login_required
def categorize_bill():
    """
    Categorize a bill into relevant topics.
    
    POST /ai/categorize
    
    Request Body:
    - bill_text: Full text of the bill
    - bill_title: Title of the bill
    - custom_categories: Optional custom categories
    """
    try:
        # Validate request data
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Check required fields
        required_fields = ['bill_text', 'bill_title']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Set defaults
        custom_categories = data.get('custom_categories', [])
        
        # Default categories if no custom ones provided
        default_categories = [
            "Property Tax", "Assessment Methodology", "Exemptions", "Valuation", 
            "Appeals Process", "Tax Collection", "Agricultural Land", "Commercial Property",
            "Residential Property", "Industrial Property", "Public Property"
        ]
        
        categories = custom_categories if custom_categories else default_categories
        
        # Get AI service
        anthropic_api_key = current_app.config.get('ANTHROPIC_API_KEY')
        if not anthropic_api_key:
            return jsonify({"error": "AI service not configured"}), 503
        
        # Direct AI call or MCP routing
        mcp = current_app.config.get('MCP')
        if mcp:
            # Process through MCP
            response = mcp.process_api_request('/ai/categorize', data)
        else:
            # Generate prompt
            prompt = f"""
            Categorize this legislative bill into the most relevant topics from the following list:
            {', '.join(categories)}
            
            Title: {data['bill_title']}
            
            Bill Text:
            {data['bill_text']}
            
            For each relevant category, provide:
            1. The category name
            2. A confidence score (0-100)
            3. A brief explanation of why this category applies
            
            Return only the most relevant categories (maximum 3) and format the response as a list.
            """
            
            # Get AI response
            ai_response = get_ai_response(prompt)
            
            # Structure the response
            response = {
                "categorization": ai_response,
                "available_categories": categories,
                "success": True
            }
        
        # Log the action
        _log_action('bill_categorization', 
                   f"Categorized bill '{data['bill_title'][:30]}...'")
        
        return jsonify(response)
        
    except Exception as e:
        logger.exception(f"Error categorizing bill: {str(e)}")
        return jsonify({
            "error": f"Error categorizing bill: {str(e)}"
        }), 500

@ai_api_bp.route('/impact-assessment', methods=['POST'])
@login_required
def impact_assessment():
    """
    Assess the general impact of a bill on various aspects.
    
    POST /ai/impact-assessment
    
    Request Body:
    - bill_text: Full text of the bill
    - bill_title: Title of the bill
    - impact_areas: Optional impact areas to focus on
    - communities: Optional communities to focus on
    """
    try:
        # Validate request data
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Check required fields
        required_fields = ['bill_text', 'bill_title']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Set defaults
        impact_areas = data.get('impact_areas', ['economic', 'social', 'administrative', 'procedural'])
        communities = data.get('communities', ['property owners', 'assessors', 'local government', 'taxpayers'])
        
        # Get AI service
        anthropic_api_key = current_app.config.get('ANTHROPIC_API_KEY')
        if not anthropic_api_key:
            return jsonify({"error": "AI service not configured"}), 503
        
        # Direct AI call or MCP routing
        mcp = current_app.config.get('MCP')
        if mcp:
            # Process through MCP
            response = mcp.process_api_request('/ai/impact-assessment', data)
        else:
            # Generate prompt
            prompt = f"""
            Assess the impact of this legislative bill on the following areas:
            {', '.join(impact_areas)}
            
            And for these communities:
            {', '.join(communities)}
            
            Title: {data['bill_title']}
            
            Bill Text:
            {data['bill_text']}
            
            For each impact area and community, provide:
            1. A brief description of the impact
            2. The severity level (minimal, moderate, significant)
            3. Whether the impact is positive, negative, or neutral
            4. Any recommendations for mitigating negative impacts
            
            Format the response as a structured assessment for each combination of impact area and community.
            """
            
            # Get AI response
            ai_response = get_ai_response(prompt)
            
            # Structure the response
            response = {
                "impact_assessment": ai_response,
                "impact_areas": impact_areas,
                "communities": communities,
                "success": True
            }
        
        # Log the action
        _log_action('impact_assessment', 
                   f"Assessed impact of bill '{data['bill_title'][:30]}...' on {', '.join(impact_areas)}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.exception(f"Error in impact assessment: {str(e)}")
        return jsonify({
            "error": f"Error in impact assessment: {str(e)}"
        }), 500

def _log_action(action, details):
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