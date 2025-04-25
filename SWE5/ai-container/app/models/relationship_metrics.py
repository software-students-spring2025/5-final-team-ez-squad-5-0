# ai-container/app/models/relationship_metrics.py (Updated)
from datetime import datetime, timedelta
import statistics

class RelationshipMetrics:
    def __init__(self, mongo_client):
        self.db = mongo_client.get_database()
    
    def calculate_metrics(self, user_id, partner_id, days=0, hours=0, minutes=0):
        """Calculate relationship metrics based on message history with flexible time window"""
        # Calculate total minutes for the time window
        total_minutes = (days * 24 * 60) + (hours * 60) + minutes
        
        # Default to 30 days if no time window specified
        if total_minutes == 0:
            days = 30
            total_minutes = days * 24 * 60
            
        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(minutes=total_minutes)
        
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
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                'time_window': {
                    'days': days,
                    'hours': hours,
                    'minutes': minutes,
                    'total_minutes': total_minutes
                }
            }
        
        # Calculate message frequency (messages per appropriate time unit)
        time_diff_hours = (end_date - start_date).total_seconds() / 3600
        
        if time_diff_hours < 1:  # Less than 1 hour window
            frequency_unit = "per minute"
            message_frequency = total_messages / max(1, time_diff_hours * 60)
        elif time_diff_hours < 24:  # Less than 1 day window
            frequency_unit = "per hour"
            message_frequency = total_messages / max(1, time_diff_hours)
        else:  # More than 1 day window
            frequency_unit = "per day"
            message_frequency = total_messages / max(1, time_diff_hours / 24)
        
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
        
        # Calculate message breakdown by sender
        user_message_count = len([msg for msg in messages if msg['sender_id'] == user_id])
        partner_message_count = total_messages - user_message_count
        
        user_percentage = (user_message_count / total_messages * 100) if total_messages > 0 else 0
        partner_percentage = (partner_message_count / total_messages * 100) if total_messages > 0 else 0
        
        # Generate insights based on the metrics
        insights = self._generate_insights(
            message_frequency, 
            avg_response_time, 
            sentiment_distribution, 
            user_percentage,
            frequency_unit
        )
        
        return {
            'message_count': total_messages,
            'user_message_count': user_message_count,
            'partner_message_count': partner_message_count,
            'user_percentage': user_percentage,
            'partner_percentage': partner_percentage,
            'avg_response_time': avg_response_time,
            'message_frequency': message_frequency,
            'frequency_unit': frequency_unit,
            'sentiment_distribution': sentiment_distribution,
            'time_window': {
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'total_minutes': total_minutes
            },
            'insights': insights
        }
    
    def _generate_insights(self, message_frequency, avg_response_time, sentiment_distribution, user_percentage, frequency_unit):
        """Generate insights based on current metrics"""
        insights = []
        
        # Adjust thresholds based on frequency unit
        freq_thresholds = {
            "per minute": {'low': 0.2, 'high': 2},
            "per hour": {'low': 3, 'high': 15},
            "per day": {'low': 5, 'high': 30}
        }
        
        # Message frequency insights
        current_thresholds = freq_thresholds.get(frequency_unit, {'low': 5, 'high': 30})
        
        if message_frequency < current_thresholds['low']:
            insights.append({
                'type': 'frequency',
                'text': 'Communication has been a bit quiet recently.',
                'suggestion': 'Try reaching out with a thoughtful message to reconnect.'
            })
        elif message_frequency > current_thresholds['high']:
            insights.append({
                'type': 'frequency',
                'text': 'You\'re communicating very frequently!',
                'suggestion': 'Quality conversations are just as important as quantity.'
            })
            
        # Response time insights (only if we have data)
        if avg_response_time is not None:
            if avg_response_time > 180:  # More than 3 hours
                insights.append({
                    'type': 'response_time',
                    'text': 'Response times have been a bit slow.',
                    'suggestion': 'Quick acknowledgments help maintain connection even when busy.'
                })
            elif avg_response_time < 5:  # Less than 5 minutes
                insights.append({
                    'type': 'response_time',
                    'text': 'You respond to each other very quickly!',
                    'suggestion': 'Your rapid responses show you prioritize each other.'
                })
            
        # Sentiment insights
        positive_percent = sentiment_distribution.get('positive', 0)
        negative_percent = sentiment_distribution.get('negative', 0)
        
        if negative_percent > 30:
            insights.append({
                'type': 'sentiment',
                'text': 'There\'s been some negative sentiment in recent messages.',
                'suggestion': 'Consider checking in with how your partner is feeling.'
            })
        elif positive_percent > 70:
            insights.append({
                'type': 'sentiment',
                'text': 'Your recent messages have very positive vibes!',
                'suggestion': 'This positive energy strengthens your connection.'
            })
            
        # Balance insights
        if user_percentage > 70:
            insights.append({
                'type': 'balance',
                'text': 'You\'re initiating most of the conversation lately.',
                'suggestion': 'Give your partner space to reach out to you.'
            })
        elif user_percentage < 30:
            insights.append({
                'type': 'balance',
                'text': 'Your partner has been initiating most conversations.',
                'suggestion': 'Consider taking the initiative to start conversations more often.'
            })
            
        return insights