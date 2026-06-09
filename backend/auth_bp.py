from flask import Blueprint, request, jsonify
import bcrypt
import jwt

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
SECRET = 'supersecret'

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    pw_hash = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
    return jsonify({"msg": "registered"})

@auth_bp.route('/login', methods=['POST'])
def login():
    token = jwt.encode({"user": "test"}, SECRET, algorithm="HS256")
    return jsonify({"token": token})

@auth_bp.route('/me', methods=['GET'])
def me():
    return jsonify({"user": "test"})
