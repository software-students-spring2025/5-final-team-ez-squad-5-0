"""
Calendar routes for the Together API
"""
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.utils.validation import validate_calendar_event

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/events', methods=['GET'])
@jwt_required()
def get_events():
    """
    Get calendar events
    ---
    tags:
      - Calendar
    security:
      - JWT: []
    parameters:
      - name: start_date
        in: query
        schema:
          type: string
          format: date
      - name: end_date
        in: query
        schema:
          type: string
          format: date
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
        description: List of calendar events
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    # Build query
    query = {'user_id': user_id}
    
    if start_date:
        query['start_time'] = {'$gte': start_date}
    
    if end_date:
        if 'start_time' not in query:
            query['start_time'] = {}
        query['start_time']['$lte'] = end_date
    
    # If user has a partner, include shared events
    if user.get('partner_id'):
        query = {
            '$or': [
                query,
                {'partner_id': user_id},
                {'user_id': user.get('partner_id'), 'shared': True}
            ]
        }
    
    # Find events
    events_cursor = mongo.db.calendar_events.find(query).sort('start_time', 1).skip(offset).limit(limit)
    
    # Convert cursor to list and format
    events = list(events_cursor)
    for event in events:
        event['_id'] = str(event['_id'])
    
    return jsonify(events), 200

@calendar_bp.route('/events', methods=['POST'])
@jwt_required()
def create_event():
    """
    Create a calendar event
    ---
    tags:
      - Calendar
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
              start_time:
                type: string
                format: date-time
              end_time:
                type: string
                format: date-time
              all_day:
                type: boolean
              location:
                type: string
              description:
                type: string
              shared:
                type: boolean
    responses:
      201:
        description: Event created
      400:
        description: Invalid request data
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get event data from request
    event_data = request.json
    
    # Validate event data
    validation_result = validate_calendar_event(event_data)
    if validation_result:
        return jsonify({'error': validation_result}), 400
    
    # Create event
    now = datetime.utcnow()
    event = {
        'event_id': str(uuid.uuid4()),
        'user_id': user_id,
        'title': event_data['title'],
        'start_time': event_data['start_time'],
        'end_time': event_data.get('end_time'),
        'all_day': event_data.get('all_day', False),
        'location': event_data.get('location', ''),
        'description': event_data.get('description', ''),
        'shared': event_data.get('shared', True),
        'created_at': now,
        'updated_at': now
    }
    
    # Add partner ID if user has a partner and event is shared
    if user.get('partner_id') and event['shared']:
        event['partner_id'] = user['partner_id']
    
    # Add recurring event properties if provided
    if event_data.get('recurring'):
        event['recurring'] = True
        event['recurrence_rule'] = event_data.get('recurrence_rule', {})
    
    # Insert event into database
    mongo.db.calendar_events.insert_one(event)
    
    # Convert ObjectId to string
    event['_id'] = str(event['_id'])
    
    return jsonify(event), 201

@calendar_bp.route('/events/<event_id>', methods=['GET'])
@jwt_required()
def get_event(event_id):
    """
    Get a specific calendar event
    ---
    tags:
      - Calendar
    security:
      - JWT: []
    parameters:
      - name: event_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Event details
      404:
        description: Event not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Find event
    event = mongo.db.calendar_events.find_one({'event_id': event_id})
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Check if user has access to event
    if event['user_id'] != user_id and event['partner_id'] != user_id and (not event.get('shared') or event['user_id'] != user.get('partner_id')):
        return jsonify({'error': 'You do not have permission to view this event'}), 403
    
    # Convert ObjectId to string
    event['_id'] = str(event['_id'])
    
    return jsonify(event), 200

@calendar_bp.route('/events/<event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """
    Update a calendar event
    ---
    tags:
      - Calendar
    security:
      - JWT: []
    parameters:
      - name: event_id
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
              start_time:
                type: string
                format: date-time
              end_time:
                type: string
                format: date-time
              all_day:
                type: boolean
              location:
                type: string
              description:
                type: string
              shared:
                type: boolean
    responses:
      200:
        description: Event updated
      400:
        description: Invalid request data
      404:
        description: Event not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find event
    event = mongo.db.calendar_events.find_one({'event_id': event_id})
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Check if user is the creator
    if event['user_id'] != user_id:
        return jsonify({'error': 'You do not have permission to update this event'}), 403
    
    # Get update data from request
    update_data = request.json
    
    # Validate update data
    if 'start_time' in update_data:
        validation_result = validate_calendar_event({
            'start_time': update_data['start_time'],
            'end_time': update_data.get('end_time', event.get('end_time')),
            'title': update_data.get('title', event['title'])
        })
        
        if validation_result:
            return jsonify({'error': validation_result}), 400
    
    # Build update document
    update_doc = {'updated_at': datetime.utcnow()}
    
    if 'title' in update_data:
        update_doc['title'] = update_data['title']
    
    if 'start_time' in update_data:
        update_doc['start_time'] = update_data['start_time']
    
    if 'end_time' in update_data:
        update_doc['end_time'] = update_data['end_time']
    
    if 'all_day' in update_data:
        update_doc['all_day'] = update_data['all_day']
    
    if 'location' in update_data:
        update_doc['location'] = update_data['location']
    
    if 'description' in update_data:
        update_doc['description'] = update_data['description']
    
    if 'shared' in update_data:
        update_doc['shared'] = update_data['shared']
        
        # Find user
        user = mongo.db.users.find_one({'user_id': user_id})
        
        # Update partner_id based on shared status
        if update_data['shared'] and user.get('partner_id'):
            update_doc['partner_id'] = user['partner_id']
        elif not update_data['shared'] and 'partner_id' in event:
            update_doc['partner_id'] = None
    
    # Update event
    mongo.db.calendar_events.update_one(
        {'event_id': event_id},
        {'$set': update_doc}
    )
    
    # Get updated event
    updated_event = mongo.db.calendar_events.find_one({'event_id': event_id})
    updated_event['_id'] = str(updated_event['_id'])
    
    return jsonify(updated_event), 200

@calendar_bp.route('/events/<event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    """
    Delete a calendar event
    ---
    tags:
      - Calendar
    security:
      - JWT: []
    parameters:
      - name: event_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Event deleted
      404:
        description: Event not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find event
    event = mongo.db.calendar_events.find_one({'event_id': event_id})
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Check if user is the creator
    if event['user_id'] != user_id:
        return jsonify({'error': 'You do not have permission to delete this event'}), 403
    
    # Delete event
    mongo.db.calendar_events.delete_one({'event_id': event_id})
    
    return jsonify({'message': 'Event deleted successfully'}), 200
