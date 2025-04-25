# ai-container/app/routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from datetime import datetime

# Import models
from .models.sentiment_analyzer import SentimentAnalyzer
from .models.relationship_metrics import RelationshipMetrics


# Initialize blueprint and models
ai_bp = Blueprint('ai', __name__)
sentiment_analyzer = SentimentAnalyzer()

# Initialize MongoDB client
from pymongo import MongoClient
import os

mongo_uri = os.environ.get('MONGO_URI', 'mongodb://db:27017/together')
mongo_client = MongoClient(mongo_uri)

# Initialize models with MongoDB client
relationship_metrics = RelationshipMetrics(mongo_client)

# Sentiment analysis endpoint
@ai_bp.route('/analyze-message', methods=['POST'])
@jwt_required()
def analyze_message():
    data = request.json
    current_user_id = get_jwt_identity()
    
    message_id = data.get('message_id')
    content = data.get('content')
    
    if not message_id or not content:
        return jsonify({'error': 'Missing message_id or content'}), 400
    
    # Analyze sentiment
    sentiment_result = sentiment_analyzer.analyze_text(content)
    
    # Store analysis result
    db = mongo_client.get_database()
    
    # Check if already analyzed
    existing = db.analyzed_messages.find_one({'message_id': message_id})
    if existing:
        db.analyzed_messages.update_one(
            {'message_id': message_id},
            {'$set': {
                'sentiment': sentiment_result['sentiment'],
                'scores': sentiment_result['scores'],
                'textblob_polarity': sentiment_result['textblob_polarity'],
                'updated_at': datetime.utcnow()
            }}
        )
    else:
        db.analyzed_messages.insert_one({
            'message_id': message_id,
            'user_id': current_user_id,
            'sentiment': sentiment_result['sentiment'],
            'scores': sentiment_result['scores'],
            'textblob_polarity': sentiment_result['textblob_polarity'],
            'created_at': datetime.utcnow()
        })
    
    return jsonify({
        'message_id': message_id,
        'analysis': sentiment_result
    }), 200

# Relationship metrics endpoint
@ai_bp.route('/relationship-metrics/<partner_id>', methods=['GET'])
@jwt_required()
def get_relationship_metrics(partner_id):
    current_user_id = get_jwt_identity()
    days = int(request.args.get('days', 30))
    
    metrics = relationship_metrics.calculate_metrics(current_user_id, partner_id, days)
    
    return jsonify({
        'user_id': current_user_id,
        'partner_id': partner_id,
        'time_period_days': days,
        'metrics': metrics
    }), 200


# Smart reminder suggestion endpoint
@ai_bp.route('/smart-reminders', methods=['GET'])
@jwt_required()
def get_smart_reminders():
    current_user_id = get_jwt_identity()
    db = mongo_client.get_database()
    
    # Get messages from the last 30 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # Find all messages where the current user is the receiver
    messages = list(db.messages.find({
        'receiver_id': current_user_id,
        'created_at': {'$gte': start_date, '$lte': end_date}
    }).sort('created_at', -1).limit(100))
    
    # Simple keyword-based extraction (in a real implementation, this would use NLP)
    date_keywords = ['tomorrow', 'next week', 'on monday', 'on tuesday', 'on wednesday', 
                     'on thursday', 'on friday', 'on saturday', 'on sunday',
                     'restaurant', 'dinner', 'lunch', 'movie', 'date', 'birthday', 'anniversary']
    
    potential_reminders = []
    
    for message in messages:
        content = message['content'].lower()
        sender_id = message['sender_id']
        
        # Try to find a sender name
        sender = db.users.find_one({'_id': ObjectId(sender_id)})
        sender_name = sender['name'] if sender else "Your partner"
        
        for keyword in date_keywords:
            if keyword in content:
                potential_reminders.append({
                    'message_id': str(message['_id']),
                    'content': message['content'],
                    'sender': sender_name,
                    'keyword': keyword,
                    'created_at': message['created_at']
                })
                break
    
    return jsonify({
        'reminders': potential_reminders[:5]  # Return top 5 potential reminders
    }), 200
