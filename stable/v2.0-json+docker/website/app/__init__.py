from flask import Flask
from .blueprints.auth import auth_bp
from .blueprints.dashboard import dashboard_bp
from .blueprints.api import api_bp
import os


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    return app
