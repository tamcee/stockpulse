"""
Authentication Blueprint — JWT-based user registration and login.
"""
import functools
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from flask import Blueprint, request, jsonify, g

from backend.config import Config
from backend.models import create_user, get_user_by_email, get_user_by_id

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def _hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def _check_password(password, hashed):
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def _generate_token(user_id):
    """Generate a signed JWT token."""
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=Config.JWT_EXPIRY_HOURS),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')


def _decode_token(token):
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login_required(f):
    """Decorator to protect routes that require authentication."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Authentication required'}), 401

        user_id = _decode_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401

        user = get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 401

        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def optional_auth(f):
    """Decorator that sets g.current_user if authenticated, but doesn't require it."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if token:
            user_id = _decode_token(token)
            if user_id:
                g.current_user = get_user_by_id(user_id)
            else:
                g.current_user = None
        else:
            g.current_user = None

        return f(*args, **kwargs)
    return decorated


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    # Validation
    if not username or len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    if not email or '@' not in email:
        return jsonify({'error': 'Valid email is required'}), 400
    if not password or len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    # Hash password and create user
    password_hash = _hash_password(password)

    try:
        user_id = create_user(username, email, password_hash)
    except ValueError as e:
        return jsonify({'error': str(e)}), 409

    token = _generate_token(user_id)

    return jsonify({
        'message': 'Registration successful',
        'token': token,
        'user': {
            'id': user_id,
            'username': username,
            'email': email,
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and return a JWT."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = get_user_by_email(email)
    if not user or not _check_password(password, user['password_hash']):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = _generate_token(user['id'])

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
        }
    })


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Return the current authenticated user."""
    return jsonify({
        'user': g.current_user
    })
