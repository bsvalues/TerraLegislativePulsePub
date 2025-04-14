import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
from utils.validators import validate_email

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Validate form data
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('auth/login.html')
        
        # Find the user
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password. Please try again.', 'danger')
            logger.warning(f"Failed login attempt for username: {username}")
            return render_template('auth/login.html')
        
        # Check if user is active
        if not user.is_active:
            flash('Your account has been deactivated. Please contact an administrator.', 'danger')
            logger.warning(f"Login attempt for deactivated account: {username}")
            return render_template('auth/login.html')
        
        # Log in the user
        login_user(user, remember=remember)
        logger.info(f"User logged in: {username}")
        
        # Redirect to the page the user was trying to access, or to the dashboard
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        else:
            return redirect(url_for('web.dashboard'))
    
    # GET request - show the login form
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    username = current_user.username
    logout_user()
    logger.info(f"User logged out: {username}")
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register a new user
    Note: In a production environment, this would typically be restricted
    to administrators or have additional security measures.
    """
    # Determine if registration is allowed
    if not current_app.config.get('ALLOW_REGISTRATION', False):
        flash('User registration is currently disabled.', 'danger')
        return redirect(url_for('auth.login'))
    
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate form data
        if not username or not email or not password or not confirm_password:
            flash('Please fill out all fields.', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        
        if not validate_email(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('auth/register.html')
        
        # Check if user already exists
        user = User.query.filter((User.username == username) | (User.email == email)).first()
        if user:
            flash('Username or email already exists.', 'danger')
            return render_template('auth/register.html')
        
        # Create the new user
        new_user = User(
            username=username,
            email=email,
            role='user'  # Default role
        )
        new_user.set_password(password)
        
        # Add and commit to the database
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"New user registered: {username}")
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    # GET request - show the registration form
    return render_template('auth/register.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            # Update profile information
            email = request.form.get('email')
            
            if not validate_email(email):
                flash('Please enter a valid email address.', 'danger')
                return render_template('auth/profile.html')
            
            # Check if email is already in use by another user
            existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
            if existing_user:
                flash('Email is already in use by another account.', 'danger')
                return render_template('auth/profile.html')
            
            # Update the user's email
            current_user.email = email
            db.session.commit()
            
            logger.info(f"User {current_user.username} updated profile information")
            flash('Profile updated successfully.', 'success')
            
        elif action == 'change_password':
            # Change password
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Validate passwords
            if not current_password or not new_password or not confirm_password:
                flash('Please fill out all password fields.', 'danger')
                return render_template('auth/profile.html')
            
            if not check_password_hash(current_user.password_hash, current_password):
                flash('Current password is incorrect.', 'danger')
                return render_template('auth/profile.html')
            
            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return render_template('auth/profile.html')
            
            # Update the password
            current_user.set_password(new_password)
            db.session.commit()
            
            logger.info(f"User {current_user.username} changed password")
            flash('Password changed successfully.', 'success')
        
        return redirect(url_for('auth.profile'))
    
    # GET request - show the profile page
    return render_template('auth/profile.html')
