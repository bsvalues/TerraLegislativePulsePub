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
@login_required
def property_impact():
    """Show property impact analysis tool"""
    # Get property classes from config
    property_classes = current_app.config.get('PROPERTY_CLASSIFICATIONS', {})
    
    # Get recent bills
    recent_bills = get_all_tracked_bills(limit=10)
    
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