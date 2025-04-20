from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson.objectid import ObjectId

# Import the mongo instance - adjust this import according to your actual structure
from .. import mongo

# Create blueprints
auth_bp = Blueprint('auth', __name__)
calendar_bp = Blueprint('calendar', __name__)
messages_bp = Blueprint('messages_bp', __name__)

# Helper functions
def get_user_by_email(email):
    user = mongo.db.users.find_one({'email': email})
    if user:
        user['_id'] = str(user['_id'])
    return user

def get_user_by_id(user_id):
    try:
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if user:
            user['_id'] = str(user['_id'])
        return user
    except:
        return None

def create_user(name, email, password):
    user = {
        'name': name,
        'email': email,
        'password_hash': generate_password_hash(password),
        'created_at': datetime.utcnow()
    }
    
    result = mongo.db.users.insert_one(user)
    user['_id'] = str(result.inserted_id)
    
    return user

# Authentication routes
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    
    # Check if email already exists
    if get_user_by_email(data['email']):
        return jsonify({'message': 'Email already registered'}), 400
    
    # Create new user
    user = create_user(data['name'], data['email'], data['password'])
    
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    
    user = get_user_by_email(data['email'])
    
    if not user or not check_password_hash(user['password_hash'], data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    # Create access token
    access_token = create_access_token(identity=str(user['_id']))
    
    return jsonify({
        'message': 'Login successful',
        'token': access_token,
        'user': user
    }), 200

# Calendar routes
@calendar_bp.route('/events', methods=['GET'])
@jwt_required()
def get_events():
    current_user_id = get_jwt_identity()
    
    events = list(mongo.db.events.find({'user_id': current_user_id}))
    for event in events:
        event['_id'] = str(event['_id'])
    
    return jsonify({'events': events}), 200

@calendar_bp.route('/events', methods=['POST'])
@jwt_required()
def create_event():
    current_user_id = get_jwt_identity()
    data = request.json
    
    event = {
        'title': data['title'],
        'description': data.get('description', ''),
        'start_time': datetime.fromisoformat(data['startTime']),
        'end_time': datetime.fromisoformat(data['endTime']),
        'user_id': current_user_id,
        'created_at': datetime.utcnow()
    }
    
    result = mongo.db.events.insert_one(event)
    event['_id'] = str(result.inserted_id)
    
    return jsonify({'message': 'Event created successfully', 'event': event}), 201

# Messages routes
@messages_bp.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    current_user_id = get_jwt_identity()
    
    messages = list(mongo.db.messages.find(
        {'$or': [{'sender_id': current_user_id}, {'receiver_id': current_user_id}]}
    ).sort('created_at', -1))
    
    for message in messages:
        message['_id'] = str(message['_id'])
    
    return jsonify({'messages': messages}), 200

@messages_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    current_user_id = get_jwt_identity()
    data = request.json
    
    message = {
        'content': data['content'],
        'sender_id': current_user_id,
        'receiver_id': data['receiverId'],
        'created_at': datetime.utcnow(),
        'is_read': False
    }
    
    result = mongo.db.messages.insert_one(message)
    message['_id'] = str(result.inserted_id)
    
    return jsonify({'message': 'Message sent successfully', 'data': message}), 201