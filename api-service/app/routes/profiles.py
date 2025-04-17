"""
Profile management routes for the Together API
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.utils.validation import validate_profile_update

profile_bp = Blueprint('profiles', __name__)

@profile_bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get user profile
    ---
    tags:
      - Profiles
    security:
      - JWT: []
    responses:
      200:
        description: User profile
      404:
        description: Profile not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user profile
    profile = mongo.db.profiles.find_one({'user_id': user_id})
    
    if not profile:
        # Check if user exists
        user = mongo.db.users.find_one({'user_id': user_id})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create empty profile if it doesn't exist
        profile = {
            'user_id': user_id,
            'bio': '',
            'interests': [],
            'preferences': {
                'date_ideas': [],
                'communication_style': '',
                'love_language': ''
            },
            'photos': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Insert profile into database
        mongo.db.profiles.insert_one(profile)
    
    # Convert ObjectId to string
    profile['_id'] = str(profile['_id'])
    
    return jsonify(profile), 200

@profile_bp.route('/', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update user profile
    ---
    tags:
      - Profiles
    security:
      - JWT: []
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              bio:
                type: string
              interests:
                type: array
                items:
                  type: string
              preferences:
                type: object
    responses:
      200:
        description: Profile updated
      400:
        description: Invalid request data
      404:
        description: Profile not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Get profile data from request
    profile_data = request.json
    
    # Validate profile data
    validation_result = validate_profile_update(profile_data)
    if validation_result:
        return jsonify({'error': validation_result}), 400
    
    # Find user profile
    profile = mongo.db.profiles.find_one({'user_id': user_id})
    
    if not profile:
        # Check if user exists
        user = mongo.db.users.find_one({'user_id': user_id})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create new profile
        profile = {
            'user_id': user_id,
            'bio': profile_data.get('bio', ''),
            'interests': profile_data.get('interests', []),
            'preferences': profile_data.get('preferences', {
                'date_ideas': [],
                'communication_style': '',
                'love_language': ''
            }),
            'photos': profile_data.get('photos', []),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Insert profile into database
        result = mongo.db.profiles.insert_one(profile)
        profile['_id'] = str(result.inserted_id)
        
        # Update user's profile_complete status
        mongo.db.users.update_one(
            {'user_id': user_id},
            {'$set': {'profile_complete': True, 'updated_at': datetime.utcnow()}}
        )
        
        return jsonify({
            'profile': profile,
            'message': 'Profile created successfully'
        }), 201
    
    # Update existing profile
    mongo.db.profiles.update_one(
        {'user_id': user_id},
        {
            '$set': {
                'bio': profile_data.get('bio', profile.get('bio', '')),
                'interests': profile_data.get('interests', profile.get('interests', [])),
                'preferences': profile_data.get('preferences', profile.get('preferences', {})),
                'photos': profile_data.get('photos', profile.get('photos', [])),
                'updated_at': datetime.utcnow()
            }
        }
    )
    
    # Update user's profile_complete status
    mongo.db.users.update_one(
        {'user_id': user_id},
        {'$set': {'profile_complete': True, 'updated_at': datetime.utcnow()}}
    )
    
    # Get updated profile
    updated_profile = mongo.db.profiles.find_one({'user_id': user_id})
    updated_profile['_id'] = str(updated_profile['_id'])
    
    return jsonify({
        'profile': updated_profile,
        'message': 'Profile updated successfully'
    }), 200

@profile_bp.route('/partner', methods=['GET'])
@jwt_required()
def get_partner_profile():
    """
    Get partner profile
    ---
    tags:
      - Profiles
    security:
      - JWT: []
    responses:
      200:
        description: Partner profile
      404:
        description: Partner not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user['partner_id']:
        return jsonify({'error': 'You are not connected with a partner'}), 404
    
    # Find partner profile
    partner_profile = mongo.db.profiles.find_one({'user_id': user['partner_id']})
    
    if not partner_profile:
        return jsonify({'error': 'Partner profile not found'}), 404
    
    # Convert ObjectId to string
    partner_profile['_id'] = str(partner_profile['_id'])
    
    return jsonify(partner_profile), 200

@profile_bp.route('/relationship', methods=['GET'])
@jwt_required()
def get_relationship():
    """
    Get relationship information
    ---
    tags:
      - Profiles
    security:
      - JWT: []
    responses:
      200:
        description: Relationship information
      404:
        description: Relationship not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user['partner_id'] or user['partner_status'] != 'connected':
        return jsonify({
            'relationship_status': user['partner_status'],
            'message': 'Not connected with a partner'
        }), 200
    
    # Find partner
    partner = mongo.db.users.find_one({'user_id': user['partner_id']})
    
    if not partner:
        return jsonify({'error': 'Partner not found'}), 404
    
    # Find relationship
    relationship = mongo.db.relationships.find_one({
        '$or': [
            {'user1_id': user_id, 'user2_id': user['partner_id']},
            {'user1_id': user['partner_id'], 'user2_id': user_id}
        ]
    })
    
    if not relationship:
        # Create relationship if it doesn't exist
        relationship = {
            'user1_id': user_id,
            'user2_id': user['partner_id'],
            'status': 'connected',
            'anniversary': datetime.utcnow(),
            'nickname1': '',
            'nickname2': '',
            'settings': {
                'privacy_level': 'private',
                'shared_calendar': True
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Insert relationship into database
        mongo.db.relationships.insert_one(relationship)
    
    # Convert ObjectId to string
    relationship['_id'] = str(relationship['_id'])
    
    # Get partner basic info (without sensitive data)
    partner_info = {
        'user_id': partner['user_id'],
        'name': partner['name'],
        'email': partner['email']
    }
    
    return jsonify({
        'relationship': relationship,
        'partner': partner_info,
        'relationship_status': 'connected'
    }), 200