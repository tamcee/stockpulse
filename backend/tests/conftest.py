import pytest
from backend.app import create_app
from backend.models import init_db
import sqlite3

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_token():
    import jwt
    return jwt.encode({"user": "test"}, "supersecret", algorithm="HS256")
