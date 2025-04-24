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
    
    # Get user to check for partner
    current_user = get_user_by_id(current_user_id)
    
    # Query for events created by the current user
    query = {'user_id': current_user_id}
    
    # If user has a connected partner, include their events too
    if current_user.get('partner_id') and current_user.get('partner_status') == 'connected':
        query = {'$or': [
            {'user_id': current_user_id},
            {'user_id': current_user.get('partner_id')}
        ]}
    
    events = list(mongo.db.events.find(query).sort('start_time', 1))
    for event in events:
        event['_id'] = str(event['_id'])
        
        # Add creator info
        if event['user_id'] == current_user_id:
            event['creator'] = 'you'
        else:
            event['creator'] = 'partner'
    
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
    
    # Get current user
    current_user = get_user_by_id(current_user_id)
    
    # Use provided receiver_id or default to partner
    receiver_id = data.get('receiverId')
    
    # If no receiver_id provided, check if user has partner
    if not receiver_id:
        if current_user.get('partner_id') and current_user.get('partner_status') == 'connected':
            receiver_id = current_user.get('partner_id')
        else:
            return jsonify({'message': 'No partner connected and no receiver specified'}), 400
    
    message = {
        'content': data['content'],
        'sender_id': current_user_id,
        'receiver_id': receiver_id,
        'created_at': datetime.utcnow(),
        'is_read': False
    }
    
    result = mongo.db.messages.insert_one(message)
    message['_id'] = str(result.inserted_id)
    
    return jsonify({'message': 'Message sent successfully', 'data': message}), 201

# NEW: Scheduled messages endpoints
@messages_bp.route('/schedule', methods=['POST'])
@jwt_required()
def schedule_message():
    current_user_id = get_jwt_identity()
    data = request.json
    
    # Convert the scheduled time string to a datetime object
    try:
        scheduled_time = datetime.fromisoformat(data['scheduledTime'])
    except ValueError:
        return jsonify({'message': 'Invalid date format for scheduled time'}), 400
    
    # Create the scheduled message object
    scheduled_message = {
        'content': data['content'],
        'sender_id': current_user_id,
        'receiver_id': data['receiverId'],
        'scheduled_time': scheduled_time,
        'created_at': datetime.utcnow(),
        'status': 'pending'  # Status can be 'pending', 'sent', or 'failed'
    }
    
    result = mongo.db.scheduled_messages.insert_one(scheduled_message)
    scheduled_message['_id'] = str(result.inserted_id)
    
    return jsonify({
        'message': 'Message scheduled successfully', 
        'data': scheduled_message
    }), 201

@messages_bp.route('/scheduled', methods=['GET'])
@jwt_required()
def get_scheduled_messages():
    current_user_id = get_jwt_identity()
    
    # Get all scheduled messages for the current user
    scheduled_messages = list(mongo.db.scheduled_messages.find(
        {'sender_id': current_user_id, 'status': 'pending'}
    ).sort('scheduled_time', 1))
    
    for message in scheduled_messages:
        message['_id'] = str(message['_id'])
        # Convert datetime objects to strings for JSON serialization
        message['scheduled_time'] = message['scheduled_time'].isoformat()
        message['created_at'] = message['created_at'].isoformat()
    
    return jsonify({'scheduled_messages': scheduled_messages}), 200

@messages_bp.route('/scheduled/<message_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_scheduled_message(message_id):
    current_user_id = get_jwt_identity()
    
    try:
        # Find and update the message to set status to 'cancelled'
        result = mongo.db.scheduled_messages.update_one(
            {'_id': ObjectId(message_id), 'sender_id': current_user_id, 'status': 'pending'},
            {'$set': {'status': 'cancelled'}}
        )
        
        if result.modified_count == 0:
            return jsonify({'message': 'No pending message found with that ID'}), 404
        
        return jsonify({'message': 'Scheduled message cancelled successfully'}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500
    
# Partner relationship endpoints
@auth_bp.route('/partner/invite', methods=['POST'])
@jwt_required()
def invite_partner():
    current_user_id = get_jwt_identity()
    data = request.json
    partner_email = data.get('partner_email')
    
    # Check if partner exists
    partner = get_user_by_email(partner_email)
    if not partner:
        return jsonify({'message': 'User with this email not found'}), 404
    
    # Check if user already has a partner
    current_user = get_user_by_id(current_user_id)
    if current_user.get('partner_id') and current_user.get('partner_status') == 'connected':
        return jsonify({'message': 'You are already connected with a partner'}), 400
    
    # Check if partner already has a different partner
    if partner.get('partner_id') and partner.get('partner_id') != current_user_id and partner.get('partner_status') == 'connected':
        return jsonify({'message': 'This user is already connected with another partner'}), 400
    
    # Update current user with pending partnership
    mongo.db.users.update_one(
        {'_id': ObjectId(current_user_id)},
        {'$set': {
            'partner_id': partner['_id'],
            'partner_status': 'pending_sent'
        }}
    )
    
    # Update partner with pending invitation
    mongo.db.users.update_one(
        {'_id': ObjectId(partner['_id'])},
        {'$set': {
            'partner_id': current_user_id,
            'partner_status': 'pending_received'
        }}
    )
    
    return jsonify({'message': 'Partnership invitation sent successfully'}), 200

@auth_bp.route('/partner/accept', methods=['POST'])
@jwt_required()
def accept_partner():
    current_user_id = get_jwt_identity()
    
    # Check if user has a pending invitation
    current_user = get_user_by_id(current_user_id)
    if not current_user.get('partner_id') or current_user.get('partner_status') != 'pending_received':
        return jsonify({'message': 'No pending partnership invitation found'}), 404
    
    partner_id = current_user.get('partner_id')
    
    # Update both users to connected status
    mongo.db.users.update_one(
        {'_id': ObjectId(current_user_id)},
        {'$set': {'partner_status': 'connected'}}
    )
    
    mongo.db.users.update_one(
        {'_id': ObjectId(partner_id)},
        {'$set': {'partner_status': 'connected'}}
    )
    
    return jsonify({'message': 'Partnership accepted successfully'}), 200

@auth_bp.route('/partner/reject', methods=['POST'])
@jwt_required()
def reject_partner():
    current_user_id = get_jwt_identity()
    
    # Check if user has a pending invitation
    current_user = get_user_by_id(current_user_id)
    if not current_user.get('partner_id'):
        return jsonify({'message': 'No partnership data found'}), 404
    
    partner_id = current_user.get('partner_id')
    
    # Remove partnership data from both users
    mongo.db.users.update_one(
        {'_id': ObjectId(current_user_id)},
        {'$unset': {'partner_id': '', 'partner_status': ''}}
    )
    
    mongo.db.users.update_one(
        {'_id': ObjectId(partner_id)},
        {'$unset': {'partner_id': '', 'partner_status': ''}}
    )
    
    return jsonify({'message': 'Partnership removed'}), 200

@auth_bp.route('/partner/status', methods=['GET'])
@jwt_required()
def get_partner_status():
    current_user_id = get_jwt_identity()
    
    # Get current user with partner info
    current_user = get_user_by_id(current_user_id)
    
    partner_data = None
    if current_user.get('partner_id'):
        partner = get_user_by_id(current_user.get('partner_id'))
        if partner:
            partner_data = {
                'id': partner['_id'],
                'name': partner['name'],
                'email': partner['email']
            }
    
    return jsonify({
        'has_partner': bool(current_user.get('partner_id')),
        'status': current_user.get('partner_status', 'none'),
        'partner': partner_data
    }), 200
