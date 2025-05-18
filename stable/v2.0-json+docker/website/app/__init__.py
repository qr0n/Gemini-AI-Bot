from flask import Flask
from .blueprints.auth import auth_bp
from .blueprints.dashboard import dashboard_bp
from .blueprints.api import api_bp
from .blueprints.landing import landing_bp
from .extensions import settings_manager
import os


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(landing_bp)

    # Initialize settings manager
    init_settings(app=app)

    return app


def init_settings(app: Flask):
    # Ensure all default settings are available
    for nugget in app.config.get("NUGGETS", []):
        for category in settings_manager.defaults.keys():
            if not settings_manager.get_settings(nugget, category):
                settings_manager.reset_settings(nugget, category)
