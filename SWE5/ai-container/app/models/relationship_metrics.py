# ai-container/app/models/relationship_metrics.py
from datetime import datetime, timedelta
import statistics

class RelationshipMetrics:
    def __init__(self, mongo_client):
        self.db = mongo_client.get_database()
    
    def calculate_metrics(self, user_id, partner_id, days=30):
        """Calculate relationship metrics based on message history"""
        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query messages between the two users
        messages = list(self.db.messages.find({
            '$or': [
                {'sender_id': user_id, 'receiver_id': partner_id},
                {'sender_id': partner_id, 'receiver_id': user_id}
            ],
            'created_at': {'$gte': start_date, '$lte': end_date}
        }).sort('created_at', 1))
        
        # Calculate metrics
        total_messages = len(messages)
        if total_messages == 0:
            return {
                'message_count': 0,
                'avg_response_time': None,
                'message_frequency': 0,
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0}
            }
        
        # Calculate message frequency (messages per day)
        days_with_messages = len(set([msg['created_at'].date() for msg in messages]))
        message_frequency = total_messages / max(1, days_with_messages)
        
        # Calculate response times
        response_times = []
        for i in range(1, len(messages)):
            if messages[i]['sender_id'] != messages[i-1]['sender_id']:
                response_time = (messages[i]['created_at'] - messages[i-1]['created_at']).total_seconds() / 60
                # Only count responses within 24 hours
                if response_time <= 24 * 60:
                    response_times.append(response_time)
        
        avg_response_time = statistics.mean(response_times) if response_times else None
        
        # Get sentiment distribution from previously analyzed messages
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        analyzed_messages = list(self.db.analyzed_messages.find({
            'message_id': {'$in': [str(msg['_id']) for msg in messages]}
        }))
        
        for analysis in analyzed_messages:
            sentiment = analysis.get('sentiment', 'neutral')
            sentiment_counts[sentiment] += 1
        
        # Convert to percentages
        total_analyzed = sum(sentiment_counts.values())
        sentiment_distribution = {
            k: (v / total_analyzed * 100 if total_analyzed > 0 else 0) 
            for k, v in sentiment_counts.items()
        }
        
        return {
            'message_count': total_messages,
            'avg_response_time': avg_response_time,
            'message_frequency': message_frequency,
            'sentiment_distribution': sentiment_distribution
        }