"""
Flask Application Factory
Creates and configures the Flask application with CORS, blueprints, and static file serving.
"""
import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from backend.config import Config
from backend.models import init_db
from backend.auth import auth_bp
from backend.stocks import stocks_bp
from backend.watchlist_api import watchlist_bp


def create_app():
    """Create and configure the Flask application."""
    # Determine paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(base_dir, 'frontend')

    app = Flask(
        __name__,
        static_folder=frontend_dir,
        static_url_path=''
    )

    app.config.from_object(Config)

    # Enable CORS for development
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize database
    init_db()

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(stocks_bp)
    app.register_blueprint(watchlist_bp)

    # Serve frontend
    @app.route('/')
    def serve_frontend():
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        file_path = os.path.join(frontend_dir, path)
        if os.path.isfile(file_path):
            return send_from_directory(frontend_dir, path)
        return send_from_directory(frontend_dir, 'index.html')

    return app
