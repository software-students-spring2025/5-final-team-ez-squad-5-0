"""
Mood tracking routes for the Together API
"""
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.utils.validation import validate_mood_entry

mood_bp = Blueprint('mood', __name__)

@mood_bp.route('/', methods=['POST'])
@jwt_required()
def log_mood():
    """
    Log a mood entry
    ---
    tags:
      - Mood
    security:
      - JWT: []
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              rating:
                type: integer
                minimum: 1
                maximum: 10
              date:
                type: string
                format: date-time
              notes:
                type: string
              tags:
                type: array
                items:
                  type: string
              share_with_partner:
                type: boolean
    responses:
      201:
        description: Mood logged
      400:
        description: Invalid request data
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get mood data from request
    mood_data = request.json
    
    # Validate mood data
    validation_result = validate_mood_entry(mood_data)
    if validation_result:
        return jsonify({'error': validation_result}), 400
    
    # Check if entry already exists for the date
    date = mood_data.get('date')
    existing_entry = mongo.db.moods.find_one({
        'user_id': user_id,
        'date': date
    })
    
    if existing_entry:
        return jsonify({'error': 'Mood entry already exists for this date'}), 400
    
    # Create mood entry
    now = datetime.utcnow()
    mood_entry = {
        'mood_id': str(uuid.uuid4()),
        'user_id': user_id,
        'rating': int(mood_data['rating']),
        'date': date,
        'notes': mood_data.get('notes', ''),
        'tags': mood_data.get('tags', []),
        'share_with_partner': mood_data.get('share_with_partner', True),
        'created_at': now,
        'updated_at': now
    }
    
    # Insert mood entry into database
    mongo.db.moods.insert_one(mood_entry)
    
    # Convert ObjectId to string
    mood_entry['_id'] = str(mood_entry['_id'])
    
    return jsonify(mood_entry), 201

@mood_bp.route('/', methods=['GET'])
@jwt_required()
def get_moods():
    """
    Get mood entries
    ---
    tags:
      - Mood
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
      - name: include_partner
        in: query
        schema:
          type: boolean
        default: true
    responses:
      200:
        description: List of mood entries
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
    include_partner = request.args.get('include_partner', 'true').lower() == 'true'
    
    # Build query
    query = {'user_id': user_id}
    
    if start_date:
        query['date'] = {'$gte': start_date}
    
    if end_date:
        if 'date' not in query:
            query['date'] = {}
        query['date']['$lte'] = end_date
    
    # Find user's mood entries
    mood_entries = list(mongo.db.moods.find(query).sort('date', -1))
    
    # If user has a partner and include_partner is true, get partner's mood entries
    if user['partner_id'] and include_partner:
        partner_query = {
            'user_id': user['partner_id'],
            'share_with_partner': True
        }
        
        if start_date:
            partner_query['date'] = {'$gte': start_date}
        
        if end_date:
            if 'date' not in partner_query:
                partner_query['date'] = {}
            partner_query['date']['$lte'] = end_date
        
        partner_entries = list(mongo.db.moods.find(partner_query).sort('date', -1))
        mood_entries.extend(partner_entries)
        
        # Sort combined entries by date
        mood_entries.sort(key=lambda x: x['date'], reverse=True)
    
    # Format entries
    for entry in mood_entries:
        entry['_id'] = str(entry['_id'])
        entry['is_partner'] = entry['user_id'] == user.get('partner_id')
    
    return jsonify(mood_entries), 200

@mood_bp.route('/today', methods=['GET'])
@jwt_required()
def get_today_mood():
    """
    Get today's mood entries
    ---
    tags:
      - Mood
    security:
      - JWT: []
    parameters:
      - name: include_partner
        in: query
        schema:
          type: boolean
        default: true
    responses:
      200:
        description: Today's mood entries
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get today's date
    today = datetime.utcnow().strftime('%Y-%m-%d')
    
    # Get filter parameters
    include_partner = request.args.get('include_partner', 'true').lower() == 'true'
    
    # Find user's mood entry for today
    user_mood = mongo.db.moods.find_one({
        'user_id': user_id,
        'date': today
    })
    
    result = {
        'user': user_mood,
        'partner': None
    }
    
    if user_mood:
        user_mood['_id'] = str(user_mood['_id'])
    
    # If user has a partner and include_partner is true, get partner's mood entry
    if user['partner_id'] and include_partner:
        partner_mood = mongo.db.moods.find_one({
            'user_id': user['partner_id'],
            'date': today,
            'share_with_partner': True
        })
        
        if partner_mood:
            partner_mood['_id'] = str(partner_mood['_id'])
            result['partner'] = partner_mood
    
    return jsonify(result), 200

@mood_bp.route('/<mood_id>', methods=['PUT'])
@jwt_required()
def update_mood(mood_id):
    """
    Update a mood entry
    ---
    tags:
      - Mood
    security:
      - JWT: []
    parameters:
      - name: mood_id
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
              rating:
                type: integer
                minimum: 1
                maximum: 10
              notes:
                type: string
              tags:
                type: array
                items:
                  type: string
              share_with_partner:
                type: boolean
    responses:
      200:
        description: Mood updated
      400:
        description: Invalid request data
      404:
        description: Mood entry not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find mood entry
    mood_entry = mongo.db.moods.find_one({'mood_id': mood_id})
    
    if not mood_entry:
        return jsonify({'error': 'Mood entry not found'}), 404
    
    # Check if user is the owner
    if mood_entry['user_id'] != user_id:
        return jsonify({'error': 'You do not have permission to update this mood entry'}), 403
    
    # Get update data from request
    update_data = request.json
    
    # Validate update data
    if 'rating' in update_data or 'date' in update_data:
        validation_result = validate_mood_entry({
            'rating': update_data.get('rating', mood_entry['rating']),
            'date': update_data.get('date', mood_entry['date'])
        })
        
        if validation_result:
            return jsonify({'error': validation_result}), 400
    
    # Build update document
    update_doc = {'updated_at': datetime.utcnow()}
    
    if 'rating' in update_data:
        update_doc['rating'] = int(update_data['rating'])
    
    if 'notes' in update_data:
        update_doc['notes'] = update_data['notes']
    
    if 'tags' in update_data:
        update_doc['tags'] = update_data['tags']
    
    if 'share_with_partner' in update_data:
        update_doc['share_with_partner'] = update_data['share_with_partner']
    
    # Update mood entry
    mongo.db.moods.update_one(
        {'mood_id': mood_id},
        {'$set': update_doc}
    )
    
    # Get updated mood entry
    updated_mood = mongo.db.moods.find_one({'mood_id': mood_id})
    updated_mood['_id'] = str(updated_mood['_id'])
    
    return jsonify(updated_mood), 200

@mood_bp.route('/<mood_id>', methods=['DELETE'])
@jwt_required()
def delete_mood(mood_id):
    """
    Delete a mood entry
    ---
    tags:
      - Mood
    security:
      - JWT: []
    parameters:
      - name: mood_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Mood entry deleted
      404:
        description: Mood entry not found
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find mood entry
    mood_entry = mongo.db.moods.find_one({'mood_id': mood_id})
    
    if not mood_entry:
        return jsonify({'error': 'Mood entry not found'}), 404
    
    # Check if user is the owner
    if mood_entry['user_id'] != user_id:
        return jsonify({'error': 'You do not have permission to delete this mood entry'}), 403
    
    # Delete mood entry
    mongo.db.moods.delete_one({'mood_id': mood_id})
    
    return jsonify({'message': 'Mood entry deleted successfully'}), 200

@mood_bp.route('/analysis', methods=['GET'])
@jwt_required()
def get_mood_analysis():
    """
    Get mood analysis
    ---
    tags:
      - Mood
    security:
      - JWT: []
    parameters:
      - name: period
        in: query
        schema:
          type: string
          enum: [week, month, year]
        default: month
      - name: include_partner
        in: query
        schema:
          type: boolean
        default: true
    responses:
      200:
        description: Mood analysis
    """
    # Get user ID from token
    user_id = get_jwt_identity()
    
    # Find user
    user = mongo.db.users.find_one({'user_id': user_id})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get filter parameters
    period = request.args.get('period', 'month')
    include_partner = request.args.get('include_partner', 'true').lower() == 'true'
    
    # Calculate date range
    today = datetime.utcnow()
    
    if period == 'week':
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    elif period == 'month':
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    elif period == 'year':
        start_date = (today - timedelta(days=365)).strftime('%Y-%m-%d')
    else:
        return jsonify({'error': 'Invalid period'}), 400
    
    end_date = today.strftime('%Y-%m-%d')
    
    # Get user's mood entries
    user_moods = list(mongo.db.moods.find({
        'user_id': user_id,
        'date': {'$gte': start_date, '$lte': end_date}
    }).sort('date', 1))
    
    # Calculate user's mood statistics
    user_stats = {
        'average_rating': 0,
        'highest_rating': 0,
        'lowest_rating': 10,
        'entries_count': len(user_moods),
        'trend': 'stable'  # 'improving', 'declining', 'stable'
    }
    
    if user_moods:
        # Calculate average
        total_rating = sum(mood['rating'] for mood in user_moods)
        user_stats['average_rating'] = round(total_rating / len(user_moods), 1)
        
        # Find highest and lowest
        user_stats['highest_rating'] = max(mood['rating'] for mood in user_moods)
        user_stats['lowest_rating'] = min(mood['rating'] for mood in user_moods)
        
        # Calculate trend (if enough data points)
        if len(user_moods) >= 3:
            first_half = user_moods[:len(user_moods)//2]
            second_half = user_moods[len(user_moods)//2:]
            
            first_avg = sum(mood['rating'] for mood in first_half) / len(first_half)
            second_avg = sum(mood['rating'] for mood in second_half) / len(second_half)
            
            if second_avg > first_avg + 0.5:
                user_stats['trend'] = 'improving'
            elif second_avg < first_avg - 0.5:
                user_stats['trend'] = 'declining'
    
    result = {
        'user': {
            'stats': user_stats,
            'entries': user_moods
        },
        'partner': None
    }
    
    # Format user's mood entries
    for mood in result['user']['entries']:
        mood['_id'] = str(mood['_id'])
    
    # If user has a partner and include_partner is true, get partner's mood stats
    if user['partner_id'] and include_partner:
        partner_moods = list(mongo.db.moods.find({
            'user_id': user['partner_id'],
            'date': {'$gte': start_date, '$lte': end_date},
            'share_with_partner': True
        }).sort('date', 1))
        
        partner_stats = {
            'average_rating': 0,
            'highest_rating': 0,
            'lowest_rating': 10,
            'entries_count': len(partner_moods),
            'trend': 'stable'
        }
        
        if partner_moods:
            # Calculate average
            total_rating = sum(mood['rating'] for mood in partner_moods)
            partner_stats['average_rating'] = round(total_rating / len(partner_moods), 1)
            
            # Find highest and lowest
            partner_stats['highest_rating'] = max(mood['rating'] for mood in partner_moods)
            partner_stats['lowest_rating'] = min(mood['rating'] for mood in partner_moods)
            
            # Calculate trend (if enough data points)
            if len(partner_moods) >= 3:
                first_half = partner_moods[:len(partner_moods)//2]
                second_half = partner_moods[len(partner_moods)//2:]
                
                first_avg = sum(mood['rating'] for mood in first_half) / len(first_half)
                second_avg = sum(mood['rating'] for mood in second_half) / len(second_half)
                
                if second_avg > first_avg + 0.5:
                    partner_stats['trend'] = 'improving'
                elif second_avg < first_avg - 0.5:
                    partner_stats['trend'] = 'declining'
        
        # Format partner's mood entries
        for mood in partner_moods:
            mood['_id'] = str(mood['_id'])
        
        result['partner'] = {
            'stats': partner_stats,
            'entries': partner_moods
        }
        
        # Calculate correlation if both have entries
        if user_moods and partner_moods:
            # Map moods by date for easier correlation calculation
            user_moods_by_date = {mood['date']: mood['rating'] for mood in user_moods}
            partner_moods_by_date = {mood['date']: mood['rating'] for mood in partner_moods}
            
            # Find common dates
            common_dates = set(user_moods_by_date.keys()) & set(partner_moods_by_date.keys())
            
            if common_dates:
                # Check if moods tend to align
                aligned_count = 0
                
                for date in common_dates:
                    user_rating = user_moods_by_date[date]
                    partner_rating = partner_moods_by_date[date]
                    
                    # Consider aligned if within 2 points
                    if abs(user_rating - partner_rating) <= 2:
                        aligned_count += 1
                
                alignment_percentage = (aligned_count / len(common_dates)) * 100
                result['correlation'] = {
                    'alignment_percentage': round(alignment_percentage, 1),
                    'common_dates_count': len(common_dates),
                    'is_aligned': alignment_percentage >= 70
                }
    
    return jsonify(result), 200