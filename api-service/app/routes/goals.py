"""
Goals routes for the Together API
"""
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.utils.validation import validate_goal

goal_bp = Blueprint('goals', __name__)

@goal_bp.route('/', methods=['GET'])
@jwt_required()
def get_goals():
    """
    Get goals
    ---
    tags:
      - Goals
    security:
      - JWT: []
    parameters:
      - name: category
        in: query
        schema:
          type: string
          enum: [relationship, personal, shared, other]
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
        description: List of goals
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get filter parameters
    category = request.args.get('category')
    completed = request.args.get('completed')
    if completed is not None:
        completed = completed.lower() == 'true'
    
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    
    # Build query
    query = {
        '$or': [
            {'user_id': user_id, 'private': True},
            {'user_id': user_id, 'private': False}
        ]
    }
    
    # Add partner's shared goals if user has a partner
    if user.get('partner_id'):
        query['$or'].append({'user_id': user['partner_id'], 'private': False})
    
    if category:
        query['category'] = category
        
    if completed is not None:
        query['completed'] = completed
    
    # Find goals
    goals_cursor = mongo.db.goals.find(query).sort('created_at', -1).skip(offset).limit(limit)
    
    # Convert cursor to list and format
    goals = list(goals_cursor)
    for goal in goals:
        goal['_id'] = str(goal['_id'])
        goal['is_partner'] = goal['user_id'] == user.get('partner_id')
    
    return jsonify(goals), 200

@goal_bp.route('/', methods=['POST'])
@jwt_required()
def create_goal():
    """
    Create a new goal
    ---
    tags:
      - Goals
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
              category:
                type: string
                enum: [relationship, personal, shared, other]
              deadline:
                type: string
                format: date-time
              private:
                type: boolean
              milestones:
                type: array
                items:
                  type: object
                  properties:
                    title:
                      type: string
                    completed:
                      type: boolean
    responses:
      201:
        description: Goal created
      400:
        description: Invalid request data
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get goal data from request
    goal_data = request.json
    
    # Validate goal data
    validation_result = validate_goal(goal_data)
    if validation_result:
        return jsonify({'error': validation_result}), 400
    
    # Create goal
    now = datetime.utcnow()
    goal = {
        'goal_id': str(uuid.uuid4()),
        'user_id': user_id,
        'title': goal_data['title'],
        'description': goal_data.get('description', ''),
        'category': goal_data['category'],
        'deadline': goal_data.get('deadline'),
        'private': goal_data.get('private', True if goal_data['category'] == 'personal' else False),
        'completed': False,
        'progress': 0,
        'created_at': now,
        'updated_at': now
    }
    
    # Add milestones if provided
    if 'milestones' in goal_data and goal_data['milestones']:
        milestones = []
        for milestone in goal_data['milestones']:
            milestones.append({
                'milestone_id': str(uuid.uuid4()),
                'title': milestone['title'],
                'completed': milestone.get('completed', False),
                'created_at': now,
                'updated_at': now
            })
        goal['milestones'] = milestones
    else:
        goal['milestones'] = []
    
    # Insert goal into database
    mongo.db.goals.insert_one(goal)
    
    # Convert ObjectId to string
    goal['_id'] = str(goal['_id'])
    
    return jsonify(goal), 201

@goal_bp.route('/<goal_id>', methods=['GET'])
@jwt_required()
def get_goal(goal_id):
    """
    Get a specific goal
    ---
    tags:
      - Goals
    security:
      - JWT: []
    parameters:
      - name: goal_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Goal details
      404:
        description: Goal not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Find goal
    goal = mongo.db.goals.find_one({'goal_id': goal_id})
    
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Check if user has access to goal
    if goal['user_id'] != user_id and (goal.get('private') or goal['user_id'] != user.get('partner_id')):
        return jsonify({'error': 'You do not have permission to view this goal'}), 403
    
    # Convert ObjectId to string
    goal['_id'] = str(goal['_id'])
    
    # Add is_partner flag
    goal['is_partner'] = goal['user_id'] == user.get('partner_id')
    
    return jsonify(goal), 200

@goal_bp.route('/<goal_id>', methods=['PUT'])
@jwt_required()
def update_goal(goal_id):
    """
    Update a goal
    ---
    tags:
      - Goals
    security:
      - JWT: []
    parameters:
      - name: goal_id
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
              category:
                type: string
                enum: [relationship, personal, shared, other]
              deadline:
                type: string
                format: date-time
              private:
                type: boolean
              completed:
                type: boolean
              progress:
                type: integer
                minimum: 0
                maximum: 100
    responses:
      200:
        description: Goal updated
      400:
        description: Invalid request data
      404:
        description: Goal not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find goal
    goal = mongo.db.goals.find_one({'goal_id': goal_id})
    
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Check if user is the creator
    if goal['user_id'] != user_id:
        return jsonify({'error': 'You do not have permission to update this goal'}), 403
    
    # Get update data from request
    update_data = request.json
    
    # Validate update data
    if 'title' in update_data or 'category' in update_data:
        validation_result = validate_goal({
            'title': update_data.get('title', goal['title']),
            'category': update_data.get('category', goal['category'])
        })
        
        if validation_result:
            return jsonify({'error': validation_result}), 400
    
    # Build update document
    update_doc = {'updated_at': datetime.utcnow()}
    
    if 'title' in update_data:
        update_doc['title'] = update_data['title']
    
    if 'description' in update_data:
        update_doc['description'] = update_data['description']
    
    if 'category' in update_data:
        update_doc['category'] = update_data['category']
    
    if 'deadline' in update_data:
        update_doc['deadline'] = update_data['deadline']
    
    if 'private' in update_data:
        update_doc['private'] = update_data['private']
    
    if 'completed' in update_data:
        update_doc['completed'] = update_data['completed']
        
        # If marked as completed, set progress to 100
        if update_data['completed']:
            update_doc['progress'] = 100
    
    if 'progress' in update_data:
        progress = int(update_data['progress'])
        if progress < 0 or progress > 100:
            return jsonify({'error': 'Progress must be between 0 and 100'}), 400
        
        update_doc['progress'] = progress
        
        # Update completed status based on progress
        if progress == 100:
            update_doc['completed'] = True
        elif 'completed' not in update_data:
            update_doc['completed'] = False
    
    # Update goal
    mongo.db.goals.update_one(
        {'goal_id': goal_id},
        {'$set': update_doc}
    )
    
    # Get updated goal
    updated_goal = mongo.db.goals.find_one({'goal_id': goal_id})
    updated_goal['_id'] = str(updated_goal['_id'])
    
    return jsonify(updated_goal), 200

@goal_bp.route('/<goal_id>/milestones', methods=['POST'])
@jwt_required()
def add_milestone(goal_id):
    """
    Add a milestone to a goal
    ---
    tags:
      - Goals
    security:
      - JWT: []
    parameters:
      - name: goal_id
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
    responses:
      201:
        description: Milestone added
      400:
        description: Invalid request data
      404:
        description: Goal not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find goal
    goal = mongo.db.goals.find_one({'goal_id': goal_id})
    
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Check if user is the creator
    if goal['user_id'] != user_id:
        return jsonify({'error': 'You do not have permission to add milestones to this goal'}), 403
    
    # Get milestone data from request
    milestone_data = request.json
    
    # Validate milestone data
    if 'title' not in milestone_data or not isinstance(milestone_data['title'], str) or len(milestone_data['title']) < 1:
        return jsonify({'error': 'Milestone title is required and must be a non-empty string'}), 400
    
    # Create milestone
    now = datetime.utcnow()
    milestone = {
        'milestone_id': str(uuid.uuid4()),
        'title': milestone_data['title'],
        'completed': False,
        'created_at': now,
        'updated_at': now
    }
    
    # Add milestone to goal
    mongo.db.goals.update_one(
        {'goal_id': goal_id},
        {
            '$push': {'milestones': milestone},
            '$set': {'updated_at': now}
        }
    )
    
    return jsonify(milestone), 201

@goal_bp.route('/<goal_id>/milestones/<milestone_id>', methods=['PUT'])
@jwt_required()
def update_milestone(goal_id, milestone_id):
    """
    Update a milestone
    ---
    tags:
      - Goals
    security:
      - JWT: []
    parameters:
      - name: goal_id
        in: path
        required: true
        schema:
          type: string
      - name: milestone_id
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
              completed:
                type: boolean
    responses:
      200:
        description: Milestone updated
      400:
        description: Invalid request data
      404:
        description: Goal or milestone not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find goal
    goal = mongo.db.goals.find_one({'goal_id': goal_id})
    
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Check if user is the creator
    if goal['user_id'] != user_id:
        return jsonify({'error': 'You do not have permission to update milestones for this goal'}), 403
    
    # Find milestone
    milestone = None
    for m in goal.get('milestones', []):
        if m.get('milestone_id') == milestone_id:
            milestone = m
            break
    
    if not milestone:
        return jsonify({'error': 'Milestone not found'}), 404
    
    # Get update data from request
    update_data = request.json
    
    # Validate update data
    if 'title' in update_data and (not isinstance(update_data['title'], str) or len(update_data['title']) < 1):
        return jsonify({'error': 'Milestone title must be a non-empty string'}), 400
    
    # Build update document
    update_fields = {}
    now = datetime.utcnow()
    
    if 'title' in update_data:
        update_fields[f'milestones.$.title'] = update_data['title']
    
    if 'completed' in update_data:
        update_fields[f'milestones.$.completed'] = update_data['completed']
    
    update_fields[f'milestones.$.updated_at'] = now
    update_fields['updated_at'] = now
    
    # Update milestone
    mongo.db.goals.update_one(
        {'goal_id': goal_id, 'milestones.milestone_id': milestone_id},
        {'$set': update_fields}
    )
    
    # If all milestones are completed, update progress
    if 'completed' in update_data and update_data['completed']:
        updated_goal = mongo.db.goals.find_one({'goal_id': goal_id})
        milestones = updated_goal.get('milestones', [])
        completed_milestones = sum(1 for m in milestones if m.get('completed'))
        
        if completed_milestones > 0 and len(milestones) > 0:
            progress = int((completed_milestones / len(milestones)) * 100)
            
            # Update goal progress
            mongo.db.goals.update_one(
                {'goal_id': goal_id},
                {
                    '$set': {
                        'progress': progress,
                        'completed': progress == 100,
                        'updated_at': now
                    }
                }
            )
    
    # Get updated goal
    updated_goal = mongo.db.goals.find_one({'goal_id': goal_id})
    
    # Get updated milestone
    updated_milestone = None
    for m in updated_goal.get('milestones', []):
        if m.get('milestone_id') == milestone_id:
            updated_milestone = m
            break
    
    return jsonify(updated_milestone), 200

@goal_bp.route('/<goal_id>', methods=['DELETE'])
@jwt_required()
def delete_goal(goal_id):
    """
    Delete a goal
    ---
    tags:
      - Goals
    security:
      - JWT: []
    parameters:
      - name: goal_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Goal deleted
      404:
        description: Goal not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find goal
    goal = mongo.db.goals.find_one({'goal_id': goal_id})
    
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Check if user is the creator
    if goal['user_id'] != user_id:
        return jsonify({'error': 'You do not have permission to delete this goal'}), 403
    
    # Delete goal
    mongo.db.goals.delete_one({'goal_id': goal_id})
    
    return jsonify({'message': 'Goal deleted successfully'}), 200

@goal_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_goal_categories():
    """
    Get goal categories
    ---
    tags:
      - Goals
    security:
      - JWT: []
    responses:
      200:
        description: List of goal categories
    """
    categories = [
        {'id': 'relationship', 'name': 'Relationship', 'description': 'Goals related to your relationship'},
        {'id': 'personal', 'name': 'Personal', 'description': 'Your individual goals'},
        {'id': 'shared', 'name': 'Shared', 'description': 'Goals you are working on together'},
        {'id': 'other', 'name': 'Other', 'description': 'Other types of goals'}
    ]
    
    return jsonify(categories), 200
