"""
Web Routes

This module contains the web routes for the Benton County Assessor AI Platform.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Property, Assessment, LegislativeUpdate, AuditLog, db
from services.trackers import get_all_tracked_bills, search_bills, get_bill_by_id
from services.bill_analysis_service import analyze_tracked_bill

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Homepage with overview of the platform"""
    return render_template('index.html')

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next', url_for('web.dashboard'))
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@web_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('web.index'))

@web_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with key metrics and recent activity"""
    # Sample metrics for the dashboard
    metrics = {
        'property_count': Property.query.count(),
        'assessment_count': Assessment.query.count(),
        'legislative_updates': LegislativeUpdate.query.count(),
        'recent_activity': AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(5).all()
    }
    
    return render_template('dashboard.html', metrics=metrics)

@web_bp.route('/legislative-tracking')
@login_required
def legislative_tracking():
    """Legislative tracking overview page"""
    # Get recent bills from all trackers
    bills = get_all_tracked_bills(limit=50)
    
    # Group by source for the UI
    bills_by_source = {}
    for bill in bills:
        source = bill.get('source', 'Unknown')
        if source not in bills_by_source:
            bills_by_source[source] = []
        bills_by_source[source].append(bill)
    
    return render_template('legislative/overview.html', 
                          bills_by_source=bills_by_source)

@web_bp.route('/legislative-tracking/search')
@login_required
def search_legislation():
    """Search for legislation across all trackers"""
    query = request.args.get('query', '')
    
    results = []
    if query:
        results = search_bills(query)
    
    return render_template('legislative/search.html', 
                          query=query, 
                          results=results)

@web_bp.route('/legislative-tracking/bill/<bill_id>')
@login_required
def view_bill(bill_id):
    """View details of a specific bill"""
    source = request.args.get('source')
    
    # Get the bill
    bill = get_bill_by_id(bill_id, source)
    
    if not bill:
        flash(f"Bill {bill_id} not found", 'warning')
        return redirect(url_for('web.legislative_tracking'))
    
    # Get analysis based on user's properties
    property_class = request.args.get('property_class')
    
    # Check if an analysis already exists, or needs to be generated
    analysis = None
    if request.args.get('analyze') == 'true':
        analysis = analyze_tracked_bill(
            bill_id=bill_id,
            source=source,
            property_class=property_class
        )
    
    return render_template('legislative/bill_detail.html', 
                          bill=bill, 
                          analysis=analysis,
                          property_class=property_class)

@web_bp.route('/properties')
@login_required
def property_list():
    """List of properties in the system"""
    properties = Property.query.all()
    return render_template('properties/list.html', properties=properties)

@web_bp.route('/properties/<property_id>')
@login_required
def property_detail(property_id):
    """Details of a specific property"""
    property = Property.query.get_or_404(property_id)
    assessments = property.assessments
    
    return render_template('properties/detail.html', 
                          property=property, 
                          assessments=assessments)

@web_bp.route('/activity-log')
@login_required
def activity_log():
    """System activity log"""
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('activity_log.html', logs=logs)

@web_bp.route('/profile')
@login_required
def user_profile():
    """User profile page"""
    return render_template('profile.html')