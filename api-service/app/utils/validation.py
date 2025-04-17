"""
Validation utilities for the Together API
"""
import re
from datetime import datetime

def validate_registration(user_data):
    """
    Validate user registration data
    
    Args:
        user_data (dict): User data to validate
        
    Returns:
        str: Error message if validation fails, None otherwise
    """
    required_fields = ['email', 'password', 'name']
    
    # Check required fields
    for field in required_fields:
        if field not in user_data:
            return f"Missing required field: {field}"
    
    # Validate email
    if not isinstance(user_data['email'], str) or not re.match(r"[^@]+@[^@]+\.[^@]+", user_data['email']):
        return "Please provide a valid email address"
    
    # Validate password
    if not isinstance(user_data['password'], str) or len(user_data['password']) < 8:
        return "Password must be at least 8 characters long"
    
    # Validate name
    if not isinstance(user_data['name'], str) or len(user_data['name']) < 1:
        return "Please provide your name"
    
    # Validate birthdate if provided
    if 'birthdate' in user_data and user_data['birthdate']:
        try:
            datetime.strptime(user_data['birthdate'], '%Y-%m-%d')
        except ValueError:
            return "Birthdate must be in the format YYYY-MM-DD"
    
    return None

def validate_login(login_data):
    """
    Validate login data
    
    Args:
        login_data (dict): Login data to validate
        
    Returns:
        str: Error message if validation fails, None otherwise
    """
    required_fields = ['email', 'password']
    
    # Check required fields
    for field in required_fields:
        if field not in login_data:
            return f"Missing required field: {field}"
    
    # Validate email
    if not isinstance(login_data['email'], str) or not re.match(r"[^@]+@[^@]+\.[^@]+", login_data['email']):
        return "Please provide a valid email address"
    
    # Validate password
    if not isinstance(login_data['password'], str) or len(login_data['password']) < 1:
        return "Please provide your password"
    
    return None

def validate_profile_update(profile_data):
    """
    Validate profile update data
    
    Args:
        profile_data (dict): Profile data to validate
        
    Returns:
        str: Error message if validation fails, None otherwise
    """
    # Check if profile data is provided
    if not profile_data:
        return "No profile data provided"
    
    # Validate bio if provided
    if 'bio' in profile_data and not isinstance(profile_data['bio'], str):
        return "Bio must be a string"
    
    # Validate interests if provided
    if 'interests' in profile_data:
        if not isinstance(profile_data['interests'], list):
            return "Interests must be a list"
        
        for interest in profile_data['interests']:
            if not isinstance(interest, str) or len(interest) < 1:
                return "Each interest must be a non-empty string"
    
    # Validate preferences if provided
    if 'preferences' in profile_data:
        if not isinstance(profile_data['preferences'], dict):
            return "Preferences must be an object"
        
        # Validate date_ideas if provided
        if 'date_ideas' in profile_data['preferences']:
            if not isinstance(profile_data['preferences']['date_ideas'], list):
                return "Date ideas must be a list"
            
            for idea in profile_data['preferences']['date_ideas']:
                if not isinstance(idea, str) or len(idea) < 1:
                    return "Each date idea must be a non-empty string"
        
        # Validate communication_style if provided
        if 'communication_style' in profile_data['preferences'] and not isinstance(profile_data['preferences']['communication_style'], str):
            return "Communication style must be a string"
        
        # Validate love_language if provided
        if 'love_language' in profile_data['preferences'] and not isinstance(profile_data['preferences']['love_language'], str):
            return "Love language must be a string"
    
    # Validate photos if provided
    if 'photos' in profile_data:
        if not isinstance(profile_data['photos'], list):
            return "Photos must be a list"
        
        for photo in profile_data['photos']:
            if not isinstance(photo, str) or len(photo) < 1:
                return "Each photo must be a non-empty string (URL)"
    
    return None

def validate_message(message_data):
    """
    Validate message data
    
    Args:
        message_data (dict): Message data to validate
        
    Returns:
        str: Error message if validation fails, None otherwise
    """
    # Check if content is provided
    if 'content' not in message_data or not isinstance(message_data['content'], str) or len(message_data['content']) < 1:
        return "Message content is required and must be a non-empty string"
    
    # Validate message type if provided
    valid_types = ['text', 'image', 'voice', 'video']
    if 'type' in message_data and message_data['type'] not in valid_types:
        return f"Message type must be one of: {', '.join(valid_types)}"
    
    # Validate scheduled_for if provided
    if 'scheduled_for' in message_data and message_data['scheduled_for']:
        try:
            datetime.fromisoformat(message_data['scheduled_for'].replace('Z', '+00:00'))
        except ValueError:
            return "scheduled_for must be a valid ISO 8601 datetime string"
    
    return None

def validate_activity(activity_data):
    """
    Validate activity data
    
    Args:
        activity_data (dict): Activity data to validate
        
    Returns:
        str: Error message if validation fails, None otherwise
    """
    required_fields = ['title', 'description', 'type']
    
    # Check required fields
    for field in required_fields:
        if field not in activity_data:
            return f"Missing required field: {field}"
    
    # Validate title
    if not isinstance(activity_data['title'], str) or len(activity_data['title']) < 1:
        return "Title must be a non-empty string"
    
    # Validate description
    if not isinstance(activity_data['description'], str):
        return "Description must be a string"
    
    # Validate type
    valid_types = ['date', 'task', 'surprise', 'game', 'other']
    if activity_data['type'] not in valid_types:
        return f"Type must be one of: {', '.join(valid_types)}"
    
    # Validate scheduled_for if provided
    if 'scheduled_for' in activity_data and activity_data['scheduled_for']:
        try:
            datetime.fromisoformat(activity_data['scheduled_for'].replace('Z', '+00:00'))
        except ValueError:
            return "scheduled_for must be a valid ISO 8601 datetime string"
    
    # Validate location if provided
    if 'location' in activity_data and not isinstance(activity_data['location'], str):
        return "Location must be a string"
    
    return None

def validate_calendar_event(event_data):
    """
    Validate calendar event data
    
    Args:
        event_data (dict): Event data to validate
        
    Returns:
        str: Error message if validation fails, None otherwise
    """
    required_fields = ['title', 'start_time']
    
    # Check required fields
    for field in required_fields:
        if field not in event_data:
            return f"Missing required field: {field}"
    
    # Validate title
    if not isinstance(event_data['title'], str) or len(event_data['title']) < 1:
        return "Title must be a non-empty string"
    
    # Validate start_time
    try:
        datetime.fromisoformat(event_data['start_time'].replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return "start_time must be a valid ISO 8601 datetime string"
    
    # Validate end_time if provided
    if 'end_time' in event_data and event_data['end_time']:
        try:
            end_time = datetime.fromisoformat(event_data['end_time'].replace('Z', '+00:00'))
            start_time = datetime.fromisoformat(event_data['start_time'].replace('Z', '+00:00'))
            
            if end_time <= start_time:
                return "end_time must be after start_time"
        except (ValueError, AttributeError):
            return "end_time must be a valid ISO 8601 datetime string"
    
    # Validate all_day if provided
    if 'all_day' in event_data and not isinstance(event_data['all_day'], bool):
        return "all_day must be a boolean"
    
    # Validate location if provided
    if 'location' in event_data and not isinstance(event_data['location'], str):
        return "Location must be a string"
    
    # Validate description if provided
    if 'description' in event_data and not isinstance(event_data['description'], str):
        return "Description must be a string"
    
    # Validate recurring if provided
    if 'recurring' in event_data and not isinstance(event_data['recurring'], bool):
        return "recurring must be a boolean"
    
    # Validate recurrence_rule if provided
    if 'recurrence_rule' in event_data and not isinstance(event_data['recurrence_rule'], dict):
        return "recurrence_rule must be an object"
    
    return None

def validate_prompt_response(response_data):
    """
    Validate prompt response data
    
    Args:
        response_data (dict): Response data to validate
        
    Returns:
        str: Error message if validation fails, None otherwise
    """
    required_fields = ['prompt_id', 'content']
    
    # Check required fields
    for field in required_fields:
        if field not in response_data:
            return f"Missing required field: {field}"
    
    # Validate prompt_id
    if not isinstance(response_data['prompt_id'], str) or len(response_data['prompt_id']) < 1:
        return "prompt_id must be a non-empty string"
    
    # Validate content
    if not isinstance(response_data['content'], str) or len(response_data['content']) < 1:
        return "Content must be a non-empty string"
    
    return None

def validate_mood_entry(mood_data):
    """
    Validate mood entry data
    
    Args:
        mood_data (dict): Mood data to validate
        
    Returns:
        str: Error message if validation fails, None otherwise
    """
    required_fields = ['rating', 'date']
    
    # Check required fields
    for field in required_fields:
        if field not in mood_data:
            return f"Missing required field: {field}"
    
    # Validate rating
    try:
        rating = int(mood_data['rating'])
        if rating < 1 or rating > 10:
            return "Rating must be between 1 and 10"
    except (ValueError, TypeError):
        return "Rating must be a number between 1 and 10"
    
    # Validate date
    try:
        datetime.fromisoformat(mood_data['date'].replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return "Date must be a valid ISO 8601 datetime string"
    
    # Validate notes if provided
    if 'notes' in mood_data and not isinstance(mood_data['notes'], str):
        return "Notes must be a string"
    
    return None

def validate_goal(goal_data):
    """
    Validate goal data
    
    Args:
        goal_data (dict): Goal data to validate
        
    Returns:
        str: Error message if validation fails, None otherwise
    """
    required_fields = ['title', 'category']
    
    # Check required fields
    for field in required_fields:
        if field not in goal_data:
            return f"Missing required field: {field}"
    
    # Validate title
    if not isinstance(goal_data['title'], str) or len(goal_data['title']) < 1:
        return "Title must be a non-empty string"
    
    # Validate category
    valid_categories = ['relationship', 'personal', 'shared', 'other']
    if goal_data['category'] not in valid_categories:
        return f"Category must be one of: {', '.join(valid_categories)}"
    
    # Validate description if provided
    if 'description' in goal_data and not isinstance(goal_data['description'], str):
        return "Description must be a string"
    
    # Validate deadline if provided
    if 'deadline' in goal_data and goal_data['deadline']:
        try:
            datetime.fromisoformat(goal_data['deadline'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return "Deadline must be a valid ISO 8601 datetime string"
    
    # Validate private if provided
    if 'private' in goal_data and not isinstance(goal_data['private'], bool):
        return "private must be a boolean"
    
    # Validate milestones if provided
    if 'milestones' in goal_data:
        if not isinstance(goal_data['milestones'], list):
            return "Milestones must be a list"
        
        for milestone in goal_data['milestones']:
            if not isinstance(milestone, dict):
                return "Each milestone must be an object"
            
            if 'title' not in milestone or not isinstance(milestone['title'], str) or len(milestone['title']) < 1:
                return "Each milestone must have a non-empty title"
    
    return None