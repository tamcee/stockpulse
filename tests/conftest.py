import os
import tempfile
import pytest
import jwt
from datetime import datetime, timedelta, timezone
from backend.app import create_app
import backend.config as config_module

@pytest.fixture(autouse=True)
def app_and_db():
    """Create and configure a new app instance, with a temporary database per test."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    
    # Globally override Config so models.py uses the temp DB
    orig_db = config_module.Config.DATABASE_PATH
    orig_key = config_module.Config.ALPHA_VANTAGE_API_KEY
    
    config_module.Config.DATABASE_PATH = db_path
    config_module.Config.ALPHA_VANTAGE_API_KEY = 'test_key'
    
    app = create_app()
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['TESTING'] = True
    
    with app.app_context():
        from backend.models import init_db
        init_db()
        yield app

    # Teardown
    config_module.Config.DATABASE_PATH = orig_db
    config_module.Config.ALPHA_VANTAGE_API_KEY = orig_key
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def app(app_and_db):
    return app_and_db

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def auth_token(app):
    """Generate a valid test token."""
    with app.app_context():
        from backend.models import create_user
        try:
            user_id = create_user('testuser', 'test@test.com', 'hashed_pass')
        except ValueError:
            user_id = 1
            
        payload = {
            'user_id': user_id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1),
            'iat': datetime.now(timezone.utc),
        }
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        return token
