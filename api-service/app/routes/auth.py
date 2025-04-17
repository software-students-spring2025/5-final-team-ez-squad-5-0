"""
Authentication routes for the Together API
"""
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo
from app.utils.validation import validate_registration, validate_login

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
              password:
                type: string
              name:
                type: string
              birthdate:
                type: string
    responses:
      201:
        description: User registered successfully
      400:
        description: Invalid request data
      409:
        description: Email already exists
    """
    user_data = request.json
    
    # Validate registration data
    validation_result = validate_registration(user_data)
    if validation_result:
        return jsonify({'error': validation_result}), 400
    
    # Check if email already exists
    if mongo.db.users.find_one({'email': user_data['email'].lower()}):
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create user document
    new_user = {
        'user_id': str(uuid.uuid4()),
        'email': user_data['email'].lower(),
        'password': generate_password_hash(user_data['password']),
        'name': user_data['name'],
        'birthdate': user_data.get('birthdate'),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'profile_complete': False,
        'partner_id': None,
        'partner_status': 'single',  # 'single', 'invited', 'connected'
        'settings': {
            'notifications': True,
            'privacy_level': 'private'
        }
    }
    
    # Insert user into database
    mongo.db.users.insert_one(new_user)
    
    # Create tokens
    access_token = create_access_token(identity=new_user['user_id'])
    refresh_token = create_refresh_token(identity=new_user['user_id'])
    
    # Return tokens and user info (without password)
    new_user.pop('password')
    
    return jsonify({
        'user': new_user,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'message': 'Registration successful'
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login
    ---
    tags:
      - Authentication
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
              password:
                type: string
    responses:
      200:
        description: Login successful
      400:
        description: Invalid request data
      401:
        description: Invalid credentials
    """
    login_data = request.json
    
    # Validate login data
    validation_result = validate_login(login_data)
    if validation_result:
        return jsonify({'error': validation_result}), 400
    
    # Find user by email
    user = mongo.db.users.find_one({'email': login_data['email'].lower()})
    
    # Check if user exists and password is correct
    if not user or not check_password_hash(user['password'], login_data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Create tokens
    access_token = create_access_token(identity=user['user_id'])
    refresh_token = create_refresh_token(identity=user['user_id'])
    
    # Return tokens and user info (without password)
    user_info = {k: v for k, v in user.items() if k != 'password'}
    user_info['_id'] = str(user_info['_id'])  # Convert ObjectId to string
    
    return jsonify({
        'user': user_info,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'message': 'Login successful'
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """
    Refresh access token
    ---
    tags:
      - Authentication
    security:
      - JWT: []
    responses:
      200:
        description: Token refreshed
      401:
        description: Invalid refresh token
    """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    
    return jsonify({
        'access_token': access_token,
        'message': 'Token refreshed successfully'
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current user information
    ---
    tags:
      - Authentication
    security:
      - JWT: []
    responses:
      200:
        description: User information
      404:
        description: User not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user by ID
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Return user info (without password)
    user_info = {k: v for k, v in user.items() if k != 'password'}
    user_info['_id'] = str(user_info['_id'])  # Convert ObjectId to string
    
    return jsonify(user_info), 200

@auth_bp.route('/invite-partner', methods=['POST'])
@jwt_required()
def invite_partner():
    """
    Invite a partner to connect
    ---
    tags:
      - Authentication
    security:
      - JWT: []
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              partner_email:
                type: string
    responses:
      200:
        description: Invitation sent successfully
      400:
        description: Invalid request data
      404:
        description: Partner not found
      409:
        description: Already connected with a partner
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user by ID
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user already has a partner
    if user['partner_status'] == 'connected':
        return jsonify({'error': 'You are already connected with a partner'}), 409
    
    # Get partner email from request
    partner_email = request.json.get('partner_email')
    
    if not partner_email:
        return jsonify({'error': 'Partner email is required'}), 400
    
    # Find partner by email
    partner = mongo.db.users.find_one({'email': partner_email.lower()})
    
    if not partner:
        return jsonify({'error': 'User with this email not found'}), 404
    
    # Check if partner already has a connection
    if partner['partner_status'] == 'connected':
        return jsonify({'error': 'This user is already connected with a partner'}), 409
    
    # Create invitation
    invitation = {
        'invitation_id': str(uuid.uuid4()),
        'sender_id': user_id,
        'receiver_id': partner['user_id'],
        'status': 'pending',  # 'pending', 'accepted', 'rejected'
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    # Insert invitation into database
    mongo.db.invitations.insert_one(invitation)
    
    # Update user and partner status
    mongo.db.users.update_one(
        {'user_id': user_id},
        {'$set': {'partner_status': 'invited', 'updated_at': datetime.utcnow()}}
    )
    
    return jsonify({
        'message': 'Partner invitation sent successfully',
        'invitation_id': invitation['invitation_id']
    }), 200