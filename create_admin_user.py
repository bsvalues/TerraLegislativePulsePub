"""
Create Admin User

This script creates an admin user for the TerraLegislativePulse platform.
"""

from werkzeug.security import generate_password_hash
from app import app
from bootstrap import db
from models import User

def create_admin_user(username, email, password):
    """Create a new admin user"""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User {username} already exists.")
            return
        
        # Create new admin user
        admin_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='admin',
            is_active=True
        )
        
        # Add to database
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"Admin user {username} created successfully.")

if __name__ == "__main__":
    create_admin_user('admin', 'admin@terralegislative.gov', 'Admin123!')