import logging
import os  # for default DB path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from mcp.master_control import MasterControlProgram
from agents.data_validation_agent import DataValidationAgent
from agents.valuation_agent import ValuationAgent
from agents.property_impact_agent import PropertyImpactAgent
from agents.user_interaction_agent import UserInteractionAgent

# Base model class for SQLAlchemy
class Base(DeclarativeBase):
    pass

# Flask extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Initialize logging
def init_logging(app: Flask):
    logging.basicConfig(level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))

# Initialize Flask extensions
def init_extensions(app: Flask):
    # SQLAlchemy engine options
    app.config.setdefault('SQLALCHEMY_ENGINE_OPTIONS', {})
    app.config['SQLALCHEMY_ENGINE_OPTIONS'].update({
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'connect_timeout': 10,
            'application_name': app.import_name
        },
        'pool_size': 10,
        'max_overflow': 15
    })
    # Ensure a database URI is set, fallback to SQLite in instance folder
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        default_db = os.path.join(app.instance_path, 'benton_local.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{default_db}'
    db.init_app(app)
    login_manager.init_app(app)
    # Proxy fix for correct URL generation behind proxies
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize MCP and register agents
def init_mcp(app: Flask):
    """Instantiate MasterControlProgram, register all agents, and attach to app"""
    mcp = MasterControlProgram()
    # Register each agent instance
    mcp.register_agent(DataValidationAgent())
    mcp.register_agent(ValuationAgent())
    mcp.register_agent(PropertyImpactAgent())
    mcp.register_agent(UserInteractionAgent())
    # Attach to Flask app
    app.extensions['mcp'] = mcp
    return mcp

# Register Flask error handlers
def register_error_handlers(app: Flask):
    @app.errorhandler(404)
    def page_not_found(e):
        return "Page not found", 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return "Internal server error", 500

# Register application blueprints and login settings
def register_blueprints(app: Flask):
    from routes.ai_api import ai_api_bp
    from routes.web import web_bp
    from routes.bill_api import bill_api_bp

    app.register_blueprint(ai_api_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(bill_api_bp)

    login_manager.login_view = 'web.login'
    login_manager.login_message_category = 'info'
