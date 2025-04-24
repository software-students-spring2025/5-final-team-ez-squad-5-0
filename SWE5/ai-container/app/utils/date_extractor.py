import re
from datetime import datetime, timedelta
import calendar

class DateExtractor:
    def __init__(self):
        # Regex patterns for date extraction
        self.today_pattern = re.compile(r'\b(today|tonight)\b', re.IGNORECASE)
        self.tomorrow_pattern = re.compile(r'\btomorrow\b', re.IGNORECASE)
        self.next_week_pattern = re.compile(r'\bnext\s+week\b', re.IGNORECASE)
        self.weekend_pattern = re.compile(r'\b(this\s+weekend|weekend)\b', re.IGNORECASE)
        self.day_pattern = re.compile(r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|thur|fri|sat|sun)\b', re.IGNORECASE)
        self.date_pattern = re.compile(r'\b(\d{1,2})[\/\.-](\d{1,2})(?:[\/\.-](\d{2,4}))?\b')
        
        # Event type patterns
        self.event_types = {
            'dinner': re.compile(r'\b(dinner|dine|eat\s+out|restaurant)\b', re.IGNORECASE),
            'lunch': re.compile(r'\b(lunch|grab\s+a\s+bite)\b', re.IGNORECASE),
            'coffee': re.compile(r'\b(coffee|cafe|tea)\b', re.IGNORECASE),
            'movie': re.compile(r'\b(movie|film|cinema|theater)\b', re.IGNORECASE),
            'date': re.compile(r'\b(date|date\s+night)\b', re.IGNORECASE),
            'meeting': re.compile(r'\b(meet|meeting|meet\s+up)\b', re.IGNORECASE),
            'call': re.compile(r'\b(call|phone|facetime|zoom|skype)\b', re.IGNORECASE),
            'appointment': re.compile(r'\b(appointment|doctor|dentist|therapy)\b', re.IGNORECASE)
        }
        
    def _get_next_day_of_week(self, target_day, from_date=None):
        """Get the next occurrence of a given day of the week"""
        if from_date is None:
            from_date = datetime.now()
            
        # Convert day name to index (0 = Monday, 6 = Sunday)
        days = {
            'monday': 0, 'mon': 0,
            'tuesday': 1, 'tue': 1,
            'wednesday': 2, 'wed': 2,
            'thursday': 3, 'thu': 3, 'thur': 3,
            'friday': 4, 'fri': 4,
            'saturday': 5, 'sat': 5,
            'sunday': 6, 'sun': 6
        }
        
        target_day = target_day.lower()
        target_idx = days.get(target_day)
        
        if target_idx is None:
            return None
            
        # Calculate days ahead
        current_idx = from_date.weekday()
        days_ahead = target_idx - current_idx
        
        # If the target day has already occurred this week, look for next week
        if days_ahead <= 0:
            days_ahead += 7
            
        return from_date + timedelta(days=days_ahead)
    
    def extract_potential_dates(self, text):
        """Extract potential dates from text"""
        if not text or not isinstance(text, str):
            return []
            
        results = []
        now = datetime.now()
        
        # Check for "today" or "tonight"
        if self.today_pattern.search(text):
            results.append({
                'date': now.date(),
                'type': 'explicit',
                'match': 'today/tonight',
                'fuzzy': False
            })
            
        # Check for "tomorrow"
        if self.tomorrow_pattern.search(text):
            tomorrow = now + timedelta(days=1)
            results.append({
                'date': tomorrow.date(),
                'type': 'explicit',
                'match': 'tomorrow',
                'fuzzy': False
            })
            
        # Check for "next week"
        if self.next_week_pattern.search(text):
            next_week = now + timedelta(days=7)
            results.append({
                'date': next_week.date(),
                'type': 'explicit',
                'match': 'next week',
                'fuzzy': True
            })
            
        # Check for "this weekend"
        if self.weekend_pattern.search(text):
            # Find the next Saturday
            days_until_saturday = (5 - now.weekday()) % 7
            if days_until_saturday == 0:
                days_until_saturday = 7  # If today is Saturday, get next Saturday
            next_saturday = now + timedelta(days=days_until_saturday)
            
            results.append({
                'date': next_saturday.date(),
                'type': 'explicit',
                'match': 'weekend',
                'fuzzy': True
            })
            
        # Check for day names
        day_matches = self.day_pattern.finditer(text)
        for match in day_matches:
            day_name = match.group(0)
            next_occurrence = self._get_next_day_of_week(day_name)
            
            if next_occurrence:
                results.append({
                    'date': next_occurrence.date(),
                    'type': 'day_name',
                    'match': day_name,
                    'fuzzy': False
                })
                
        # Check for date patterns (MM/DD or MM-DD)
        date_matches = self.date_pattern.finditer(text)
        for match in date_matches:
            month = int(match.group(1))
            day = int(match.group(2))
            
            # Handle year if provided
            if match.group(3):
                year = int(match.group(3))
                # Handle two-digit years
                if year < 100:
                    year += 2000
            else:
                # Default to current year
                year = now.year
                
                # If the date is in the past, assume next year
                if month < now.month or (month == now.month and day < now.day):
                    year += 1
                    
            # Validate date
            try:
                # Check if month and day are valid
                if 1 <= month <= 12 and 1 <= day <= calendar.monthrange(year, month)[1]:
                    date_obj = datetime(year, month, day).date()
                    results.append({
                        'date': date_obj,
                        'type': 'numeric',
                        'match': match.group(0),
                        'fuzzy': False
                    })
            except ValueError:
                # Invalid date, skip it
                pass
                
        return results
        
    def extract_events(self, text):
        """Extract potential events with dates from text"""
        dates = self.extract_potential_dates(text)
        
        if not dates:
            return []
            
        events = []
        
        # Try to determine event type
        event_type = 'general'
        for etype, pattern in self.event_types.items():
            if pattern.search(text):
                event_type = etype
                break
                
        # Create event objects
        for date_info in dates:
            events.append({
                'date': date_info['date'],
                'event_type': event_type,
                'fuzzy': date_info['fuzzy'],
                'text': text
            })
            
        return events
    
    def extract_smart_reminders(self, messages, user_id=None):
        """
        Extract smart reminders from a list of messages
        If user_id is provided, only extract reminders where user is the receiver
        """
        reminders = []
        
        for message in messages:
            # If user_id is specified, only include messages sent to that user
            if user_id and message.get('receiver_id') != user_id:
                continue
                
            content = message.get('content', '')
            sender_id = message.get('sender_id')
            created_at = message.get('created_at', datetime.now())
            
            # Extract events from message
            events = self.extract_events(content)
            
            for event in events:
                # Only include future events
                if event['date'] >= datetime.now().date():
                    reminders.append({
                        'message_id': str(message.get('_id')),
                        'sender_id': sender_id,
                        'created_at': created_at,
                        'event_date': event['date'],
                        'event_type': event['event_type'],
                        'is_fuzzy': event['fuzzy'],
                        'message_text': content
                    })
        
        # Sort by event date
        reminders.sort(key=lambda x: x['event_date'])
        
        return reminders