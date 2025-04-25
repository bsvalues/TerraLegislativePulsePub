"""
Web Routes

This module contains the routes for the web interface of the Benton County Assessor AI Platform.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import User, LegislativeUpdate, db
from services.bill_search_service import get_all_tracked_bills, search_bills, get_bill_by_id, search_relevant_bills
from services.bill_analysis_service import analyze_tracked_bill, categorize_bill

logger = logging.getLogger(__name__)

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Render the homepage"""
    return render_template('index.html')

@web_bp.route('/dashboard')
@login_required
def dashboard():
    """Render the main dashboard"""
    return render_template('dashboard.html')

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next', url_for('web.dashboard'))
            return redirect(next_page)
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@web_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    return redirect(url_for('web.index'))

@web_bp.route('/bills')
@login_required
def bills():
    """Show all tracked bills"""
    # Get query parameters
    search_query = request.args.get('query', '')
    source_filter = request.args.get('source', '')
    
    # Get bills
    if search_query:
        sources = [source_filter] if source_filter else None
        bills_data = search_bills(search_query, sources)
    else:
        bills_data = get_all_tracked_bills(limit=50)
    
    # Get unique sources for filter dropdown
    sources = db.session.query(LegislativeUpdate.source).distinct().all()
    sources = [source[0] for source in sources]
    
    return render_template('bills.html', 
                          bills=bills_data, 
                          sources=sources,
                          current_query=search_query,
                          current_source=source_filter)
                          
@web_bp.route('/bills/update', methods=['GET', 'POST'])
@login_required
def update_bills():
    """Update legislative bills from all sources"""
    try:
        from services.trackers import update_all_bills
        update_results = update_all_bills()
        
        total_updated = sum(update_results.values())
        if total_updated > 0:
            flash(f"Successfully updated {total_updated} bills from all sources.", "success")
        else:
            flash("No new bills were found.", "info")
        
    except Exception as e:
        logger.exception(f"Error updating bills: {str(e)}")
        flash(f"Error updating bills: {str(e)}", "danger")
    
    return redirect(url_for('web.bills'))

@web_bp.route('/bills/<bill_id>')
@login_required
def bill_detail(bill_id):
    """Show details for a specific bill"""
    # Get source from query parameter
    source = request.args.get('source', '')
    
    # Get bill data
    bill = get_bill_by_id(bill_id, source)
    
    if not bill:
        flash(f'Bill {bill_id} not found')
        return redirect(url_for('web.bills'))
    
    # Get impact analysis
    analysis = analyze_tracked_bill(bill_id, 'impact', source=source)
    
    return render_template('bill_detail.html', 
                          bill=bill, 
                          analysis=analysis)

@web_bp.route('/property-impact')
def property_impact():
    """Show property impact analysis tool"""
    # Get property classes from config
    property_classes = current_app.config.get('PROPERTY_CLASSIFICATIONS', {})
    
    # Get recent bills with error handling for database connection issues
    try:
        recent_bills = get_all_tracked_bills(limit=10)
    except Exception as e:
        logger.error(f"Database error when fetching bills: {str(e)}")
        recent_bills = []
        flash("Unable to retrieve recent legislative bills. Please try again later.", "warning")
    
    return render_template('property_impact.html',
                          property_classes=property_classes,
                          recent_bills=recent_bills)

@web_bp.route('/relevant-bills')
@login_required
def relevant_bills():
    """Show bills relevant to a specific property class"""
    # Get query parameters
    property_class = request.args.get('property_class', 'Residential')
    keywords = request.args.get('keywords', '')
    
    # Convert keywords to list
    keyword_list = [k.strip() for k in keywords.split(',')] if keywords else None
    
    # Get relevant bills
    bills_data = search_relevant_bills(property_class, keyword_list)
    
    # Get property classes from config
    property_classes = current_app.config.get('PROPERTY_CLASSIFICATIONS', {})
    
    return render_template('relevant_bills.html',
                          bills=bills_data,
                          property_classes=property_classes,
                          current_class=property_class,
                          current_keywords=keywords)

@web_bp.route('/property-validation', methods=['GET', 'POST'])
def property_validation():
    """Validate property data according to Washington State standards"""
    property_data = None
    validation_results = None
    
    if request.method == 'POST':
        # Extract form data
        property_data = {
            'parcel_id': request.form.get('parcel_id'),
            'property_address': request.form.get('property_address'),
            'property_city': request.form.get('property_city'),
            'property_state': request.form.get('property_state', 'WA'),
            'property_zip': request.form.get('property_zip'),
            'property_class': request.form.get('property_class'),
            'land_area': request.form.get('land_area'),
            'building_area': request.form.get('building_area'),
            'year_built': request.form.get('year_built'),
            'bedrooms': request.form.get('bedrooms'),
            'bathrooms': request.form.get('bathrooms'),
            'assessment_year': request.form.get('assessment_year'),
            'assessed_value': request.form.get('assessed_value'),
            'land_value': request.form.get('land_value'),
            'improvement_value': request.form.get('improvement_value'),
            'valuation_method': request.form.get('valuation_method')
        }
        
        # Send validation request through MCP
        from mcp.message_protocol import MCPMessage
        mcp = current_app.extensions['mcp']
        message = MCPMessage(
            message_type='property_validation',
            sender='web',
            data={'property_data': property_data}
        )
        response = mcp.route_message(message)
        
        # Extract validation results
        if response.success:
            validation_results = response.data.get('validation_results')
        else:
            flash(f"Validation error: {response.error}", "danger")
    
    # Get property classes from config
    property_classes = current_app.config.get('PROPERTY_CLASSIFICATIONS', {})
    
    return render_template('property_validation.html',
                          property_data=property_data,
                          validation_results=validation_results,
                          property_classes=property_classes)

@web_bp.route('/property-valuation', methods=['GET', 'POST'])
def property_valuation():
    """Calculate property value using multiple approaches"""
    property_data = None
    valuation_results = None
    
    if request.method == 'POST':
        # Extract form data
        property_data = {
            'parcel_id': request.form.get('parcel_id'),
            'property_address': request.form.get('property_address'),
            'property_city': request.form.get('property_city'),
            'property_state': request.form.get('property_state', 'WA'),
            'property_zip': request.form.get('property_zip'),
            'property_class': request.form.get('property_class'),
            'land_area': request.form.get('land_area'),
            'building_area': request.form.get('building_area'),
            'year_built': request.form.get('year_built'),
            'bedrooms': request.form.get('bedrooms'),
            'bathrooms': request.form.get('bathrooms')
        }
        
        approach = request.form.get('valuation_approach', 'market')
        
        # Send valuation request through MCP
        from mcp.message_protocol import MCPMessage
        mcp = current_app.extensions['mcp']
        message = MCPMessage(
            message_type='property_valuation',
            sender='web',
            data={'property_data': property_data, 'approach': approach}
        )
        response = mcp.route_message(message)
        
        if response.success:
            valuation_results = response.data.get('valuation_results')
        else:
            flash(f"Valuation error: {response.error}", "danger")
    
    # Get property classes and valuation methods from config
    property_classes = current_app.config.get('PROPERTY_CLASSIFICATIONS', {})
    valuation_methods = current_app.config.get('VALUATION_METHODS', ['Market', 'Cost', 'Income'])
    
    return render_template('property_valuation.html',
                          property_data=property_data,
                          valuation_results=valuation_results,
                          property_classes=property_classes,
                          valuation_methods=valuation_methods)