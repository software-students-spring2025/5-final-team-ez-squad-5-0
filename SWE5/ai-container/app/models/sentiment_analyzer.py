# ai-container/app/models/sentiment_analyzer.py
from textblob import TextBlob
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    def __init__(self):
        # Download necessary NLTK data
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')
        
        self.sia = SentimentIntensityAnalyzer()
    
    def analyze_text(self, text):
        """Analyze the sentiment of a text message"""
        # Get sentiment scores
        scores = self.sia.polarity_scores(text)
        
        # Get TextBlob sentiment for additional insight
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        
        # Determine overall sentiment
        if scores['compound'] >= 0.05:
            sentiment = 'positive'
        elif scores['compound'] <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
            
        return {
            'sentiment': sentiment,
            'scores': scores,
            'textblob_polarity': textblob_polarity
        }