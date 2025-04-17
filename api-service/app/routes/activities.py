"""
Activity routes for the Together API
"""
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.utils.validation import validate_activity

activity_bp = Blueprint('activities', __name__)

@activity_bp.route('/', methods=['GET'])
@jwt_required()
def get_activities():
    """
    Get activities for the relationship
    ---
    tags:
      - Activities
    security:
      - JWT: []
    parameters:
      - name: type
        in: query
        schema:
          type: string
          enum: [date, task, surprise, game, other]
      - name: completed
        in: query
        schema:
          type: boolean
      - name: limit
        in: query
        schema:
          type: integer
        default: 20
      - name: offset
        in: query
        schema:
          type: integer
        default: 0
    responses:
      200:
        description: List of activities
      404:
        description: Relationship not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user['partner_id']:
        return jsonify({'error': 'You are not connected with a partner'}), 404
    
    # Get filter parameters
    activity_type = request.args.get('type')
    completed = request.args.get('completed')
    if completed is not None:
        completed = completed.lower() == 'true'
    
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    
    # Build query
    query = {
        '$or': [
            {'creator_id': user_id, 'shared': True},
            {'creator_id': user['partner_id'], 'shared': True},
            {'creator_id': user_id, 'shared': False},
        ]
    }
    
    if activity_type:
        query['type'] = activity_type
        
    if completed is not None:
        query['completed'] = completed
    
    # Find activities
    activities_cursor = mongo.db.activities.find(query).sort('created_at', -1).skip(offset).limit(limit)
    
    # Convert cursor to list and format
    activities = list(activities_cursor)
    for activity in activities:
        activity['_id'] = str(activity['_id'])
    
    return jsonify(activities), 200

@activity_bp.route('/', methods=['POST'])
@jwt_required()
def create_activity():
    """
    Create a new activity
    ---
    tags:
      - Activities
    security:
      - JWT: []
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              title:
                type: string
              description:
                type: string
              type:
                type: string
                enum: [date, task, surprise, game, other]
              scheduled_for:
                type: string
                format: date-time
              location:
                type: string
              shared:
                type: boolean
    responses:
      201:
        description: Activity created
      400:
        description: Invalid request data
      404:
        description: User not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get activity data from request
    activity_data = request.json
    
    # Validate activity data
    validation_result = validate_activity(activity_data)
    if validation_result:
        return jsonify({'error': validation_result}), 400
    
    # Create activity
    now = datetime.utcnow()
    activity = {
        'activity_id': str(uuid.uuid4()),
        'creator_id': user_id,
        'title': activity_data['title'],
        'description': activity_data['description'],
        'type': activity_data['type'],
        'scheduled_for': activity_data.get('scheduled_for'),
        'location': activity_data.get('location', ''),
        'shared': activity_data.get('shared', True),
        'completed': False,
        'completion_date': None,
        'created_at': now,
        'updated_at': now
    }
    
    # Insert activity into database
    mongo.db.activities.insert_one(activity)
    
    # Create calendar event if scheduled
    if activity['scheduled_for'] and activity['shared']:
        calendar_event = {
            'event_id': str(uuid.uuid4()),
            'user_id': user_id,
            'partner_id': user.get('partner_id'),
            'title': f"Activity: {activity['title']}",
            'start_time': activity['scheduled_for'],
            'end_time': None,  # Can be updated later
            'all_day': False,
            'location': activity['location'],
            'description': activity['description'],
            'activity_id': activity['activity_id'],
            'created_at': now,
            'updated_at': now
        }
        
        mongo.db.calendar_events.insert_one(calendar_event)
    
    # Convert ObjectId to string
    activity['_id'] = str(activity['_id'])
    
    return jsonify(activity), 201

@activity_bp.route('/<activity_id>', methods=['GET'])
@jwt_required()
def get_activity(activity_id):
    """
    Get a specific activity
    ---
    tags:
      - Activities
    security:
      - JWT: []
    parameters:
      - name: activity_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Activity details
      404:
        description: Activity not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Find activity
    activity = mongo.db.activities.find_one({'activity_id': activity_id})
    
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404
    
    # Check if user has access to activity
    if activity['creator_id'] != user_id and (not activity['shared'] or activity['creator_id'] != user.get('partner_id')):
        return jsonify({'error': 'You do not have permission to view this activity'}), 403
    
    # Convert ObjectId to string
    activity['_id'] = str(activity['_id'])
    
    return jsonify(activity), 200

@activity_bp.route('/<activity_id>', methods=['PUT'])
@jwt_required()
def update_activity(activity_id):
    """
    Update an activity
    ---
    tags:
      - Activities
    security:
      - JWT: []
    parameters:
      - name: activity_id
        in: path
        required: true
        schema:
          type: string
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              title:
                type: string
              description:
                type: string
              type:
                type: string
                enum: [date, task, surprise, game, other]
              scheduled_for:
                type: string
                format: date-time
              location:
                type: string
              shared:
                type: boolean
    responses:
      200:
        description: Activity updated
      400:
        description: Invalid request data
      404:
        description: Activity not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find activity
    activity = mongo.db.activities.find_one({'activity_id': activity_id})
    
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404
    
    # Check if user is the creator
    if activity['creator_id'] != user_id:
        return jsonify({'error': 'You do not have permission to update this activity'}), 403
    
    # Get update data from request
    update_data = request.json
    
    # Validate update data
    validation_result = validate_activity(update_data)
    if validation_result:
        return jsonify({'error': validation_result}), 400
    
    # Update activity
    mongo.db.activities.update_one(
        {'activity_id': activity_id},
        {
            '$set': {
                'title': update_data['title'],
                'description': update_data['description'],
                'type': update_data['type'],
                'scheduled_for': update_data.get('scheduled_for'),
                'location': update_data.get('location', ''),
                'shared': update_data.get('shared', activity['shared']),
                'updated_at': datetime.utcnow()
            }
        }
    )
    
    # Update calendar event if exists
    if update_data.get('scheduled_for'):
        calendar_event = mongo.db.calendar_events.find_one({'activity_id': activity_id})
        
        if calendar_event:
            mongo.db.calendar_events.update_one(
                {'activity_id': activity_id},
                {
                    '$set': {
                        'title': f"Activity: {update_data['title']}",
                        'start_time': update_data['scheduled_for'],
                        'location': update_data.get('location', ''),
                        'description': update_data['description'],
                        'updated_at': datetime.utcnow()
                    }
                }
            )
    
    # Get updated activity
    updated_activity = mongo.db.activities.find_one({'activity_id': activity_id})
    updated_activity['_id'] = str(updated_activity['_id'])
    
    return jsonify(updated_activity), 200

@activity_bp.route('/<activity_id>/complete', methods=['PUT'])
@jwt_required()
def complete_activity(activity_id):
    """
    Mark an activity as completed
    ---
    tags:
      - Activities
    security:
      - JWT: []
    parameters:
      - name: activity_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Activity marked as completed
      404:
        description: Activity not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Find activity
    activity = mongo.db.activities.find_one({'activity_id': activity_id})
    
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404
    
    # Check if user has access to activity
    if activity['creator_id'] != user_id and (not activity['shared'] or activity['creator_id'] != user.get('partner_id')):
        return jsonify({'error': 'You do not have permission to complete this activity'}), 403
    
    # Mark activity as completed
    now = datetime.utcnow()
    mongo.db.activities.update_one(
        {'activity_id': activity_id},
        {
            '$set': {
                'completed': True,
                'completion_date': now,
                'updated_at': now
            }
        }
    )
    
    # Get updated activity
    updated_activity = mongo.db.activities.find_one({'activity_id': activity_id})
    updated_activity['_id'] = str(updated_activity['_id'])
    
    return jsonify(updated_activity), 200

@activity_bp.route('/<activity_id>', methods=['DELETE'])
@jwt_required()
def delete_activity(activity_id):
    """
    Delete an activity
    ---
    tags:
      - Activities
    security:
      - JWT: []
    parameters:
      - name: activity_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Activity deleted
      404:
        description: Activity not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find activity
    activity = mongo.db.activities.find_one({'activity_id': activity_id})
    
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404
    
    # Check if user is the creator
    if activity['creator_id'] != user_id:
        return jsonify({'error': 'You do not have permission to delete this activity'}), 403
    
    # Delete activity
    mongo.db.activities.delete_one({'activity_id': activity_id})
    
    # Delete associated calendar event if exists
    mongo.db.calendar_events.delete_one({'activity_id': activity_id})
    
    return jsonify({'message': 'Activity deleted successfully'}), 200

@activity_bp.route('/suggested', methods=['GET'])
@jwt_required()
def get_suggested_activities():
    """
    Get suggested activities based on preferences
    ---
    tags:
      - Activities
    security:
      - JWT: []
    parameters:
      - name: type
        in: query
        schema:
          type: string
          enum: [date, task, surprise, game, other]
      - name: limit
        in: query
        schema:
          type: integer
        default: 5
    responses:
      200:
        description: List of suggested activities
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get filter parameters
    activity_type = request.args.get('type', 'date')
    limit = int(request.args.get('limit', 5))
    
    # Build query for suggested activities
    query = {'type': activity_type, 'suggested': True}
    
    # Get user and partner profiles for preferences
    user_profile = mongo.db.profiles.find_one({'user_id': user_id})
    
    if user['partner_id']:
        partner_profile = mongo.db.profiles.find_one({'user_id': user['partner_id']})
    else:
        partner_profile = None
    
    # Build interests list from profiles
    interests = []
    if user_profile and 'interests' in user_profile:
        interests.extend(user_profile['interests'])
    
    if partner_profile and 'interests' in partner_profile:
        interests.extend(partner_profile['interests'])
    
    if interests:
        # Find suggested activities matching interests
        suggested_activities = list(mongo.db.activity_suggestions.find({
            'type': activity_type,
            'tags': {'$in': interests}
        }).limit(limit))
        
        # If not enough matching activities, get generic ones
        if len(suggested_activities) < limit:
            more_activities = list(mongo.db.activity_suggestions.find({
                'type': activity_type,
                'tags': {'$nin': interests}
            }).limit(limit - len(suggested_activities)))
            
            suggested_activities.extend(more_activities)
    else:
        # If no interests, get generic activities
        suggested_activities = list(mongo.db.activity_suggestions.find({'type': activity_type}).limit(limit))
    
    # Format activities
    for activity in suggested_activities:
        activity['_id'] = str(activity['_id'])
    
    return jsonify(suggested_activities), 200