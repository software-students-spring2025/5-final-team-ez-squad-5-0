from textblob import TextBlob
import re
from datetime import datetime, timedelta

class MessageProcessor:
    def __init__(self, mongo_client):
        self.db = mongo_client.get_database()
        
    def analyze_sentiment(self, message_text):
        """
        Analyze the sentiment of a message
        Returns: positive, negative, or neutral along with confidence score
        """
        if not message_text or not isinstance(message_text, str):
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0
            }
            
        # Use TextBlob for sentiment analysis
        blob = TextBlob(message_text)
        
        # Get polarity score (-1 to 1)
        polarity = blob.sentiment.polarity
        
        # Get subjectivity score (0 to 1) - how subjective vs objective the text is
        subjectivity = blob.sentiment.subjectivity
        
        # Determine sentiment
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
            
        # Convert polarity to a 0-1 score
        score = (polarity + 1) / 2
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': subjectivity,
            'raw_polarity': polarity
        }
    
    def store_message_analysis(self, message_id, analysis_result):
        """Store message analysis in database"""
        # Check if message has already been analyzed
        existing = self.db.analyzed_messages.find_one({'message_id': message_id})
        
        if existing:
            # Update existing analysis
            self.db.analyzed_messages.update_one(
                {'message_id': message_id},
                {'$set': {
                    'sentiment': analysis_result['sentiment'],
                    'score': analysis_result['score'],
                    'confidence': analysis_result['confidence'],
                    'updated_at': datetime.utcnow()
                }}
            )
        else:
            # Create new analysis record
            self.db.analyzed_messages.insert_one({
                'message_id': message_id,
                'sentiment': analysis_result['sentiment'],
                'score': analysis_result['score'],
                'confidence': analysis_result['confidence'],
                'created_at': datetime.utcnow()
            })
    
    def get_relationship_metrics(self, user_id, partner_id, days=30):
        """Calculate relationship metrics based on messages"""
        # Define time period
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get all messages between the two users
        messages = list(self.db.messages.find({
            '$or': [
                {'sender_id': user_id, 'receiver_id': partner_id},
                {'sender_id': partner_id, 'receiver_id': user_id}
            ],
            'created_at': {'$gte': start_date, '$lte': end_date}
        }).sort('created_at', 1))
        
        if not messages:
            return {
                'message_count': 0,
                'response_rate': 0,
                'avg_response_time_minutes': 0,
                'sentiment_score': 0.5,  # Neutral
                'message_frequency_per_day': 0
            }
        
        # Calculate basic metrics
        total_messages = len(messages)
        
        # Messages per day
        days_with_messages = set()
        for msg in messages:
            days_with_messages.add(msg['created_at'].strftime('%Y-%m-%d'))
        
        days_active = len(days_with_messages)
        messages_per_day = total_messages / max(1, days_active)
        
        # Calculate response times and rates
        response_times = []
        total_responses = 0
        
        for i in range(1, len(messages)):
            current_msg = messages[i]
            prev_msg = messages[i-1]
            
            # If sender changed, it's a response
            if current_msg['sender_id'] != prev_msg['sender_id']:
                # Calculate response time in minutes
                time_diff = (current_msg['created_at'] - prev_msg['created_at']).total_seconds() / 60
                
                # Only count if response within 24 hours (1440 minutes)
                if time_diff <= 1440:
                    total_responses += 1
                    response_times.append(time_diff)
        
        # Get average response time
        avg_response_time = sum(response_times) / max(1, len(response_times))
        
        # Calculate response rate (responses / messages that could be responded to)
        potential_responses = 0
        for i in range(len(messages) - 1):
            # If this message is followed by another message from the same person,
            # it's not counted in potential responses
            if messages[i]['sender_id'] != messages[i+1]['sender_id']:
                potential_responses += 1
                
        response_rate = total_responses / max(1, potential_responses) * 100
        
        # Analyze sentiment
        analyzed_messages = list(self.db.analyzed_messages.find({
            'message_id': {'$in': [str(msg['_id']) for msg in messages]}
        }))
        
        # Calculate average sentiment
        if analyzed_messages:
            sentiment_scores = [msg.get('score', 0.5) for msg in analyzed_messages]
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        else:
            avg_sentiment = 0.5  # Neutral if no analyzed messages
            
        # Return metrics
        return {
            'message_count': total_messages,
            'response_rate': response_rate,
            'avg_response_time_minutes': avg_response_time,
            'sentiment_score': avg_sentiment,
            'message_frequency_per_day': messages_per_day
        }
        
    def get_relationship_insights(self, metrics):
        """Generate relationship insights based on metrics"""
        insights = []
        
        # Message frequency insights
        if metrics['message_frequency_per_day'] < 1:
            insights.append({
                'type': 'frequency',
                'text': 'You could strengthen your connection by communicating more regularly.',
                'suggestion': 'Try setting aside a few minutes each day to check in with each other.'
            })
        elif metrics['message_frequency_per_day'] > 20:
            insights.append({
                'type': 'frequency',
                'text': 'You communicate frequently throughout the day!',
                'suggestion': 'Quality matters as much as quantity. Try asking deeper questions occasionally.'
            })
            
        # Response time insights
        if metrics['avg_response_time_minutes'] > 180:  # More than 3 hours
            insights.append({
                'type': 'response_time',
                'text': 'Your average response time is a bit slow.',
                'suggestion': 'Quick replies, even if brief, help maintain connection.'
            })
        elif metrics['avg_response_time_minutes'] < 5:  # Less than 5 minutes
            insights.append({
                'type': 'response_time',
                'text': 'You respond to each other very quickly!',
                'suggestion': 'Your rapid responses show you prioritize each other.'
            })
            
        # Response rate insights
        if metrics['response_rate'] < 70:
            insights.append({
                'type': 'response_rate',
                'text': 'Some messages aren\'t getting responses.',
                'suggestion': 'Try to acknowledge every message, even with a simple emoji.'
            })
        elif metrics['response_rate'] > 95:
            insights.append({
                'type': 'response_rate',
                'text': 'You\'re great at responding to each other!',
                'suggestion': 'Your consistent communication builds trust.'
            })
            
        # Sentiment insights
        if metrics['sentiment_score'] < 0.4:
            insights.append({
                'type': 'sentiment',
                'text': 'Your recent messages have been trending negative.',
                'suggestion': 'Try sharing a positive experience or expressing gratitude for something specific.'
            })
        elif metrics['sentiment_score'] > 0.7:
            insights.append({
                'type': 'sentiment',
                'text': 'Your messages show a very positive tone!',
                'suggestion': 'Keep up the positivity - it strengthens your bond.'
            })
            
        return insights
    
    def analyze_message_batch(self, user_id=None, limit=100):
        """Analyze a batch of unanalyzed messages"""
        query = {}
        if user_id:
            query['$or'] = [{'sender_id': user_id}, {'receiver_id': user_id}]
            
        # Find messages that haven't been analyzed yet
        analyzed_ids = set(item['message_id'] for item in self.db.analyzed_messages.find({}, {'message_id': 1}))
        
        messages = self.db.messages.find(query).sort('created_at', -1).limit(limit)
        
        analyzed_count = 0
        
        for message in messages:
            message_id = str(message['_id'])
            
            # Skip already analyzed messages
            if message_id in analyzed_ids:
                continue
                
            # Analyze sentiment
            analysis = self.analyze_sentiment(message.get('content', ''))
            
            # Store analysis
            self.store_message_analysis(message_id, analysis)
            
            analyzed_count += 1
            
        return analyzed_count