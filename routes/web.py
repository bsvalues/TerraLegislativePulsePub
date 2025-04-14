import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models import Property, Assessment, LegislativeUpdate, db
from services.wa_legislature_service import get_recent_wa_bills
from services.legiscan_service import search_bills

logger = logging.getLogger(__name__)

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))
    return render_template('index.html')

@web_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    # Get some summary statistics
    property_count = Property.query.count()
    assessment_count = Assessment.query.count()
    
    # Get recent legislative updates
    legislative_updates = LegislativeUpdate.query.order_by(LegislativeUpdate.created_at.desc()).limit(5).all()
    
    # Get MCP status
    mcp = current_app.config['MCP']
    mcp_status = mcp.get_status()
    
    return render_template(
        'dashboard.html',
        property_count=property_count,
        assessment_count=assessment_count,
        legislative_updates=legislative_updates,
        mcp_status=mcp_status
    )

@web_bp.route('/property-validation', methods=['GET', 'POST'])
@login_required
def property_validation():
    """Property data validation interface"""
    validation_results = None
    property_data = None
    
    if request.method == 'POST':
        # Handle form submission for property validation
        property_data = {
            'parcel_id': request.form.get('parcel_id'),
            'property_address': request.form.get('property_address'),
            'property_city': request.form.get('property_city'),
            'property_state': request.form.get('property_state', 'WA'),
            'property_zip': request.form.get('property_zip'),
            'assessment_year': int(request.form.get('assessment_year')) if request.form.get('assessment_year') else None,
            'assessed_value': float(request.form.get('assessed_value')) if request.form.get('assessed_value') else None,
            'land_value': float(request.form.get('land_value')) if request.form.get('land_value') else None,
            'improvement_value': float(request.form.get('improvement_value')) if request.form.get('improvement_value') else None,
            'property_class': request.form.get('property_class'),
            'property_class_code': request.form.get('property_class_code')
        }
        
        # Add property-class specific fields
        if property_data['property_class'] == 'Residential':
            property_data.update({
                'bedrooms': int(request.form.get('bedrooms')) if request.form.get('bedrooms') else None,
                'bathrooms': float(request.form.get('bathrooms')) if request.form.get('bathrooms') else None,
                'year_built': int(request.form.get('year_built')) if request.form.get('year_built') else None,
                'land_area': float(request.form.get('land_area')) if request.form.get('land_area') else None
            })
        elif property_data['property_class'] == 'Commercial':
            property_data.update({
                'building_area': float(request.form.get('building_area')) if request.form.get('building_area') else None,
                'land_area': float(request.form.get('land_area')) if request.form.get('land_area') else None,
                'income_approach': request.form.get('income_approach'),
                'cap_rate': float(request.form.get('cap_rate')) if request.form.get('cap_rate') else None,
                'annual_income': float(request.form.get('annual_income')) if request.form.get('annual_income') else None
            })
        else:
            # For other property classes, add common fields
            property_data.update({
                'land_area': float(request.form.get('land_area')) if request.form.get('land_area') else None
            })
        
        # Get the MCP instance
        mcp = current_app.config['MCP']
        
        # Create data for the MCP request
        data = {
            'property_data': property_data
        }
        
        # Process the request
        response = mcp.process_api_request('/api/mcp/property-validate', data)
        
        if response.get('success'):
            validation_results = response.get('data', {}).get('validation_results')
            if validation_results and not validation_results.get('has_errors'):
                if validation_results.get('has_warnings'):
                    flash('Property data validation passed with warnings.', 'warning')
                else:
                    flash('Property data validation successful!', 'success')
            elif validation_results:
                flash('Property data has validation errors.', 'danger')
        else:
            flash(f"Error validating property data: {response.get('error')}", 'danger')
    
    # Get property classifications from config
    property_classifications = current_app.config.get('PROPERTY_CLASSIFICATIONS', {})
    property_classes = property_classifications.keys()
    
    return render_template(
        'property_validation.html',
        property_data=property_data,
        validation_results=validation_results,
        property_classes=property_classes,
        property_classifications=property_classifications
    )

@web_bp.route('/property-valuation', methods=['GET', 'POST'])
@login_required
def property_valuation():
    """Property valuation interface"""
    valuation_results = None
    property_data = None
    selected_approach = 'market'
    
    if request.method == 'POST':
        # Handle form submission for property valuation
        property_data = {
            'parcel_id': request.form.get('parcel_id'),
            'property_address': request.form.get('property_address'),
            'assessment_year': int(request.form.get('assessment_year')) if request.form.get('assessment_year') else None,
            'assessed_value': float(request.form.get('assessed_value')) if request.form.get('assessed_value') else None,
            'property_class': request.form.get('property_class'),
            'year_built': int(request.form.get('year_built')) if request.form.get('year_built') else None,
            'building_area': float(request.form.get('building_area')) if request.form.get('building_area') else None,
            'land_area': float(request.form.get('land_area')) if request.form.get('land_area') else None
        }
        
        # Get the valuation approach
        selected_approach = request.form.get('valuation_approach', 'market')
        
        # Get the MCP instance
        mcp = current_app.config['MCP']
        
        # Create data for the MCP request
        data = {
            'property_data': property_data,
            'valuation_approach': selected_approach
        }
        
        # Process the request
        response = mcp.process_api_request('/api/mcp/property-value', data)
        
        if response.get('success'):
            valuation_results = response.get('data', {}).get('valuation_results')
            flash(f"Property valuation using {selected_approach} approach successful!", 'success')
        else:
            flash(f"Error calculating property value: {response.get('error')}", 'danger')
    
    # Get property classifications and valuation methods from config
    property_classes = current_app.config.get('PROPERTY_CLASSIFICATIONS', {}).keys()
    valuation_methods = current_app.config.get('VALUATION_METHODS', ['Market', 'Cost', 'Income'])
    
    return render_template(
        'property_valuation.html',
        property_data=property_data,
        valuation_results=valuation_results,
        property_classes=property_classes,
        valuation_methods=valuation_methods,
        selected_approach=selected_approach
    )

@web_bp.route('/legislative-impact', methods=['GET', 'POST'])
@login_required
def legislative_impact():
    """Legislative impact analysis interface"""
    impact_analysis = None
    bill_data = None
    analysis_type = 'bill'
    
    if request.method == 'POST':
        # Handle form submission for legislative impact analysis
        analysis_type = request.form.get('analysis_type', 'bill')
        
        # Get the MCP instance
        mcp = current_app.config['MCP']
        
        if analysis_type == 'bill':
            # Analyze impact of a specific bill
            bill_id = request.form.get('bill_id')
            
            if not bill_id:
                flash('Please enter a bill ID for analysis.', 'warning')
                return render_template('legislative_impact.html', analysis_type=analysis_type)
            
            # Create data for the MCP request
            data = {
                'analysis_type': 'bill',
                'bill_id': bill_id
            }
            
            # Process the request
            response = mcp.process_api_request('/api/mcp/property-impact', data)
            
            if response.get('success'):
                impact_analysis = response.get('data', {}).get('impact_analysis')
                bill_data = response.get('data', {}).get('bill_data')
                flash(f"Impact analysis for {bill_id} completed successfully!", 'success')
            else:
                flash(f"Error analyzing bill impact: {response.get('error')}", 'danger')
        
        elif analysis_type == 'property_class':
            # Analyze impact on a specific property class
            property_class = request.form.get('property_class')
            
            if not property_class:
                flash('Please select a property class for analysis.', 'warning')
                return render_template('legislative_impact.html', analysis_type=analysis_type)
            
            # Create data for the MCP request
            data = {
                'analysis_type': 'property_class',
                'property_class': property_class
            }
            
            # Process the request
            response = mcp.process_api_request('/api/mcp/property-impact', data)
            
            if response.get('success'):
                impact_analysis = response.get('data', {}).get('class_impact')
                flash(f"Impact analysis for {property_class} properties completed successfully!", 'success')
            else:
                flash(f"Error analyzing property class impact: {response.get('error')}", 'danger')
        
        elif analysis_type == 'overview':
            # Provide an overview of recent legislative changes
            data = {
                'analysis_type': 'overview'
            }
            
            # Process the request
            response = mcp.process_api_request('/api/mcp/property-impact', data)
            
            if response.get('success'):
                impact_analysis = response.get('data', {}).get('legislative_overview')
                flash("Legislative overview generated successfully!", 'success')
            else:
                flash(f"Error generating legislative overview: {response.get('error')}", 'danger')
    
    # Get recent bills from WA Legislature for dropdown
    recent_bills = get_recent_wa_bills(limit=10)
    
    # Get property classifications from config
    property_classes = current_app.config.get('PROPERTY_CLASSIFICATIONS', {}).keys()
    
    return render_template(
        'legislative_impact.html',
        impact_analysis=impact_analysis,
        bill_data=bill_data,
        analysis_type=analysis_type,
        recent_bills=recent_bills,
        property_classes=property_classes
    )

@web_bp.route('/user-query', methods=['GET', 'POST'])
@login_required
def user_query():
    """Natural language user query interface"""
    query_response = None
    
    if request.method == 'POST':
        # Handle form submission for user query
        query = request.form.get('query')
        
        if not query:
            flash('Please enter a query.', 'warning')
            return render_template('user_query.html')
        
        # Get additional context if provided
        context = {}
        property_id = request.form.get('property_id')
        if property_id:
            context['property_id'] = property_id
        
        # Get the MCP instance
        mcp = current_app.config['MCP']
        
        # Create data for the MCP request
        data = {
            'query': query,
            'context': context
        }
        
        # Process the request
        response = mcp.process_api_request('/api/mcp/user-query', data)
        
        if response.get('success'):
            query_response = response.get('data')
            flash("Query processed successfully!", 'success')
        else:
            flash(f"Error processing query: {response.get('error')}", 'danger')
    
    return render_template(
        'user_query.html',
        query_response=query_response
    )
