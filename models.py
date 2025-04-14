from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parcel_id = db.Column(db.String(20), unique=True, nullable=False)
    property_address = db.Column(db.String(255), nullable=False)
    property_city = db.Column(db.String(100), nullable=False)
    property_state = db.Column(db.String(2), nullable=False, default='WA')
    property_zip = db.Column(db.String(10), nullable=False)
    property_class = db.Column(db.String(50), nullable=False)
    land_area = db.Column(db.Float)
    building_area = db.Column(db.Float)
    year_built = db.Column(db.Integer)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with assessments
    assessments = db.relationship('Assessment', backref='property', lazy=True)
    
    def __repr__(self):
        return f'<Property {self.parcel_id}>'

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    assessment_year = db.Column(db.Integer, nullable=False)
    assessed_value = db.Column(db.Float, nullable=False)
    land_value = db.Column(db.Float, nullable=False)
    improvement_value = db.Column(db.Float, nullable=False)
    market_value = db.Column(db.Float)
    valuation_method = db.Column(db.String(50))
    assessment_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Assessment {self.property_id} - {self.assessment_year}>'

class LegislativeUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    source = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255))
    status = db.Column(db.String(50))
    introduced_date = db.Column(db.Date)
    last_action_date = db.Column(db.Date)
    impact_summary = db.Column(db.Text)
    affected_property_classes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<LegislativeUpdate {self.bill_id}>'

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with user
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.id} - {self.action}>'
