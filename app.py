import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the Base class
db = SQLAlchemy(model_class=Base)

# Initialize the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "benton_county_assessor_default_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

# Setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import and register blueprints
from routes.web import web_bp
from routes.api import api_bp
from routes.auth import auth_bp
from routes.ai_api import ai_api_bp
from routes.bill_api import bill_api_bp

app.register_blueprint(web_bp)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(ai_api_bp, url_prefix='/api')
app.register_blueprint(bill_api_bp, url_prefix='/api')

# Initialize MCP
from mcp.master_control import MasterControlProgram
from agents.data_validation_agent import DataValidationAgent
from agents.valuation_agent import ValuationAgent
from agents.user_interaction_agent import UserInteractionAgent
from agents.property_impact_agent import PropertyImpactAgent

with app.app_context():
    # Create database tables
    from models import User, Property, Assessment, LegislativeUpdate, AuditLog
    db.create_all()
    
    # Initialize MCP and register agents
    mcp = MasterControlProgram()
    mcp.register_agent(DataValidationAgent())
    mcp.register_agent(ValuationAgent())
    mcp.register_agent(UserInteractionAgent())
    mcp.register_agent(PropertyImpactAgent())
    
    # Make MCP available to the application
    app.config['MCP'] = mcp
    
    # Configure Anthropic API key
    app.config['ANTHROPIC_API_KEY'] = os.environ.get('ANTHROPIC_API_KEY')
    app.config['ANTHROPIC_MODEL'] = "claude-3-5-sonnet-20241022"  # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
    
    # Configure external APIs for trackers
    app.config['LEGISCAN_API_KEY'] = os.environ.get('LEGISCAN_API_KEY')
    app.config['OPENSTATES_API_KEY'] = os.environ.get('OPENSTATES_API_KEY')
    
    # Initialize legislative trackers
    from services.trackers import initialize_trackers
    initialize_trackers()
    
    # Start the legislative tracker scheduler in background
    try:
        from scheduler import start_scheduler_thread
        scheduler_thread = start_scheduler_thread()
        logger.info("Legislative tracker scheduler started successfully")
    except Exception as e:
        logger.error(f"Error starting legislative tracker scheduler: {str(e)}")
    
    logger.info("Benton County Assessor AI Platform initialized successfully")
