from flask import Flask
import os
from config import Config
from bootstrap import init_logging, init_extensions, register_error_handlers, register_blueprints, db, login_manager

# Create app
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # Initialize logging
    init_logging(app)
    # Initialize extensions
    init_extensions(app)
    # Register error handlers
    register_error_handlers(app)
    # Initialize MCP and register agents
    from bootstrap import init_mcp
    init_mcp(app)
    # Create database tables and initialize trackers
    with app.app_context():
        import models  # noqa: F401
        db.create_all()
        from services.trackers import initialize_trackers
        initialize_trackers()
    # Register blueprints and login settings
    register_blueprints(app)
    # Debug routes
    @app.route('/debug/routes')
    def debug_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                "endpoint": rule.endpoint,
                "methods": list(rule.methods),
                "path": rule.rule
            })
        return {"routes": routes}
    return app

# Create the app instance
app = create_app()

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)