"""
Prompts routes for the Together API
"""
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.utils.validation import validate_prompt_response

prompt_bp = Blueprint('prompts', __name__)

@prompt_bp.route('/', methods=['GET'])
@jwt_required()
def get_prompts():
    """
    Get conversation prompts
    ---
    tags:
      - Prompts
    security:
      - JWT: []
    parameters:
      - name: category
        in: query
        schema:
          type: string
          enum: [fun, deep, daily, growth, intimacy, goals, history]
      - name: completed
        in: query
        schema:
          type: boolean
      - name: limit
        in: query
        schema:
          type: integer
        default: 10
      - name: offset
        in: query
        schema:
          type: integer
        default: 0
    responses:
      200:
        description: List of prompts
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
    
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    
    # Build query
    query = {}
    
    if category:
        query['category'] = category
    
    # Find prompts
    prompts_cursor = mongo.db.prompts.find(query).sort('created_at', -1).skip(offset).limit(limit)
    prompts = list(prompts_cursor)
    
    # Check which prompts have been answered
    if user['partner_id']:
        for prompt in prompts:
            # Check if either user has answered this prompt
            response = mongo.db.prompt_responses.find_one({
                'prompt_id': prompt['prompt_id'],
                '$or': [
                    {'user_id': user_id},
                    {'user_id': user['partner_id']}
                ]
            })
            
            prompt['answered'] = response is not None
            prompt['_id'] = str(prompt['_id'])
    else:
        for prompt in prompts:
            # Check if user has answered this prompt
            response = mongo.db.prompt_responses.find_one({
                'prompt_id': prompt['prompt_id'],
                'user_id': user_id
            })
            
            prompt['answered'] = response is not None
            prompt['_id'] = str(prompt['_id'])
    
    # If completed filter is provided, filter prompts
    if completed is not None:
        prompts = [p for p in prompts if p.get('answered') == completed]
    
    return jsonify(prompts), 200

@prompt_bp.route('/daily', methods=['GET'])
@jwt_required()
def get_daily_prompt():
    """
    Get daily conversation prompt
    ---
    tags:
      - Prompts
    security:
      - JWT: []
    responses:
      200:
        description: Daily prompt
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if there's a daily prompt already assigned
    today = datetime.utcnow().strftime('%Y-%m-%d')
    daily_prompt = mongo.db.daily_prompts.find_one({
        'date': today,
        '$or': [
            {'user_id': user_id},
            {'relationship_id': {'$exists': True, '$ne': None}}
        ]
    })
    
    if daily_prompt:
        # Get the prompt details
        prompt = mongo.db.prompts.find_one({'prompt_id': daily_prompt['prompt_id']})
        
        if prompt:
            prompt['_id'] = str(prompt['_id'])
            
            # Check if prompt has been answered
            if user['partner_id']:
                response = mongo.db.prompt_responses.find_one({
                    'prompt_id': prompt['prompt_id'],
                    '$or': [
                        {'user_id': user_id},
                        {'user_id': user['partner_id']}
                    ]
                })
            else:
                response = mongo.db.prompt_responses.find_one({
                    'prompt_id': prompt['prompt_id'],
                    'user_id': user_id
                })
            
            prompt['answered'] = response is not None
            
            return jsonify(prompt), 200
    
    # No daily prompt assigned yet, pick a random one
    # Prefer prompts that haven't been answered
    if user['partner_id']:
        # Find responses from both user and partner
        answered_prompts = list(mongo.db.prompt_responses.find({
            '$or': [
                {'user_id': user_id},
                {'user_id': user['partner_id']}
            ]
        }).distinct('prompt_id'))
    else:
        # Find responses from user only
        answered_prompts = list(mongo.db.prompt_responses.find({
            'user_id': user_id
        }).distinct('prompt_id'))
    
    # Find a prompt that hasn't been answered
    prompt = mongo.db.prompts.find_one({
        'prompt_id': {'$nin': answered_prompts},
        'category': 'daily'
    })
    
    # If all daily prompts have been answered, pick a random one
    if not prompt:
        prompt = mongo.db.prompts.find_one({'category': 'daily'})
    
    if prompt:
        # Mark as daily prompt
        daily_prompt = {
            'date': today,
            'prompt_id': prompt['prompt_id'],
            'user_id': user_id,
            'created_at': datetime.utcnow()
        }
        
        # If user has a partner, associate with relationship
        if user['partner_id']:
            # Find relationship
            relationship = mongo.db.relationships.find_one({
                '$or': [
                    {'user1_id': user_id, 'user2_id': user['partner_id']},
                    {'user1_id': user['partner_id'], 'user2_id': user_id}
                ]
            })
            
            if relationship:
                daily_prompt['relationship_id'] = relationship.get('_id')
                daily_prompt.pop('user_id', None)
        
        # Insert daily prompt
        mongo.db.daily_prompts.insert_one(daily_prompt)
        
        prompt['_id'] = str(prompt['_id'])
        prompt['answered'] = False
        
        return jsonify(prompt), 200
    
    return jsonify({'error': 'No prompts available'}), 404

@prompt_bp.route('/<prompt_id>/responses', methods=['POST'])
@jwt_required()
def respond_to_prompt(prompt_id):
    """
    Respond to a conversation prompt
    ---
    tags:
      - Prompts
    security:
      - JWT: []
    parameters:
      - name: prompt_id
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
              content:
                type: string
    responses:
      201:
        description: Response recorded
      400:
        description: Invalid request data
      404:
        description: Prompt not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Find prompt
    prompt = mongo.db.prompts.find_one({'prompt_id': prompt_id})
    
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    # Get response data from request
    response_data = request.json
    
    # Validate response data
    validation_result = validate_prompt_response({
        'prompt_id': prompt_id,
        'content': response_data.get('content', '')
    })
    
    if validation_result:
        return jsonify({'error': validation_result}), 400
    
    # Check if user has already responded to this prompt
    existing_response = mongo.db.prompt_responses.find_one({
        'prompt_id': prompt_id,
        'user_id': user_id
    })
    
    if existing_response:
        return jsonify({'error': 'You have already responded to this prompt'}), 400
    
    # Create response
    now = datetime.utcnow()
    response = {
        'response_id': str(uuid.uuid4()),
        'prompt_id': prompt_id,
        'user_id': user_id,
        'content': response_data['content'],
        'created_at': now,
        'updated_at': now
    }
    
    # Insert response into database
    mongo.db.prompt_responses.insert_one(response)
    
    # Convert ObjectId to string
    response['_id'] = str(response['_id'])
    
    return jsonify(response), 201

@prompt_bp.route('/<prompt_id>/responses', methods=['GET'])
@jwt_required()
def get_prompt_responses(prompt_id):
    """
    Get responses to a conversation prompt
    ---
    tags:
      - Prompts
    security:
      - JWT: []
    parameters:
      - name: prompt_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: List of responses
      404:
        description: Prompt not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Find prompt
    prompt = mongo.db.prompts.find_one({'prompt_id': prompt_id})
    
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    # Find responses
    query = {'prompt_id': prompt_id}
    
    if user['partner_id']:
        # Find responses from both user and partner
        query['user_id'] = {'$in': [user_id, user['partner_id']]}
    else:
        # Find responses from user only
        query['user_id'] = user_id
    
    responses = list(mongo.db.prompt_responses.find(query).sort('created_at', 1))
    
    # Format responses
    for response in responses:
        response['_id'] = str(response['_id'])
        
        # Add user info
        response_user = mongo.db.users.find_one({'user_id': response['user_id']})
        if response_user:
            response['user_name'] = response_user['name']
            response['is_partner'] = response['user_id'] == user.get('partner_id')
    
    return jsonify(responses), 200

@prompt_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_prompt_categories():
    """
    Get available prompt categories
    ---
    tags:
      - Prompts
    security:
      - JWT: []
    responses:
      200:
        description: List of categories
    """
    categories = [
        {'id': 'fun', 'name': 'Fun & Playful', 'description': 'Lighthearted questions to bring joy and laughter'},
        {'id': 'deep', 'name': 'Deep Connection', 'description': 'Thoughtful questions to deepen your understanding of each other'},
        {'id': 'daily', 'name': 'Daily Check-in', 'description': 'Regular check-ins to stay connected day-to-day'},
        {'id': 'growth', 'name': 'Growth & Future', 'description': 'Questions about your future and growth as individuals and as a couple'},
        {'id': 'intimacy', 'name': 'Intimacy', 'description': 'Questions to enhance emotional and physical intimacy'},
        {'id': 'goals', 'name': 'Goals & Dreams', 'description': 'Discussions about your aspirations and how to support each other'},
        {'id': 'history', 'name': 'Relationship History', 'description': 'Reflect on your journey together and cherish memories'}
    ]
    
    return jsonify(categories), 200