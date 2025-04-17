"""
Messaging routes for the Together API
"""
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.utils.validation import validate_message

message_bp = Blueprint('messages', __name__)

@message_bp.route('/', methods=['GET'])
@jwt_required()
def get_messages():
    """
    Get messages between partners
    ---
    tags:
      - Messages
    security:
      - JWT: []
    parameters:
      - name: limit
        in: query
        schema:
          type: integer
        default: 50
      - name: offset
        in: query
        schema:
          type: integer
        default: 0
    responses:
      200:
        description: List of messages
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
    
    # Get pagination parameters
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    # Find messages between partners
    messages_cursor = mongo.db.messages.find({
        '$or': [
            {'sender_id': user_id, 'receiver_id': user['partner_id']},
            {'sender_id': user['partner_id'], 'receiver_id': user_id}
        ]
    }).sort('created_at', -1).skip(offset).limit(limit)
    
    # Convert cursor to list and format
    messages = list(messages_cursor)
    for message in messages:
        message['_id'] = str(message['_id'])
    
    return jsonify(messages), 200

@message_bp.route('/', methods=['POST'])
@jwt_required()
def send_message():
    """
    Send a message to partner
    ---
    tags:
      - Messages
    security:
      - JWT: []
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              content:
                type: string
              type:
                type: string
                enum: [text, image, voice, video]
              scheduled_for:
                type: string
                format: date-time
    responses:
      201:
        description: Message sent
      400:
        description: Invalid request data
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
    
    # Get message data from request
    message_data = request.json
    
    # Validate message data
    validation_result = validate_message(message_data)
    if validation_result:
        return jsonify({'error': validation_result}), 400
    
    # Create message
    now = datetime.utcnow()
    message = {
        'message_id': str(uuid.uuid4()),
        'sender_id': user_id,
        'receiver_id': user['partner_id'],
        'content': message_data['content'],
        'type': message_data.get('type', 'text'),
        'scheduled_for': message_data.get('scheduled_for'),
        'delivered': message_data.get('scheduled_for') is None,
        'read': False,
        'created_at': now,
        'updated_at': now
    }
    
    # Insert message into database
    mongo.db.messages.insert_one(message)
    
    # Convert ObjectId to string
    message['_id'] = str(message['_id'])
    
    return jsonify(message), 201

@message_bp.route('/<message_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(message_id):
    """
    Mark a message as read
    ---
    tags:
      - Messages
    security:
      - JWT: []
    parameters:
      - name: message_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Message marked as read
      404:
        description: Message not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find message
    message = mongo.db.messages.find_one({'message_id': message_id})
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    # Check if user is the receiver
    if message['receiver_id'] != user_id:
        return jsonify({'error': 'You are not authorized to mark this message as read'}), 403
    
    # Mark message as read
    mongo.db.messages.update_one(
        {'message_id': message_id},
        {'$set': {'read': True, 'updated_at': datetime.utcnow()}}
    )
    
    return jsonify({'message': 'Message marked as read'}), 200

@message_bp.route('/scheduled', methods=['GET'])
@jwt_required()
def get_scheduled_messages():
    """
    Get scheduled messages
    ---
    tags:
      - Messages
    security:
      - JWT: []
    responses:
      200:
        description: List of scheduled messages
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find scheduled messages
    scheduled_messages = list(mongo.db.messages.find({
        'sender_id': user_id,
        'scheduled_for': {'$ne': None},
        'delivered': False
    }).sort('scheduled_for', 1))
    
    # Format messages
    for message in scheduled_messages:
        message['_id'] = str(message['_id'])
    
    return jsonify(scheduled_messages), 200

@message_bp.route('/scheduled/<message_id>', methods=['DELETE'])
@jwt_required()
def cancel_scheduled_message(message_id):
    """
    Cancel a scheduled message
    ---
    tags:
      - Messages
    security:
      - JWT: []
    parameters:
      - name: message_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Scheduled message canceled
      404:
        description: Message not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find message
    message = mongo.db.messages.find_one({
        'message_id': message_id,
        'sender_id': user_id,
        'scheduled_for': {'$ne': None},
        'delivered': False
    })
    
    if not message:
        return jsonify({'error': 'Scheduled message not found'}), 404
    
    # Delete message
    mongo.db.messages.delete_one({'message_id': message_id})
    
    return jsonify({'message': 'Scheduled message canceled'}), 200