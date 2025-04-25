# ai-container/app/socket_events.py
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
from . import socketio
from .models.relationship_metrics import RelationshipMetrics
from pymongo import MongoClient
import os
import json
from datetime import datetime

# Initialize MongoDB client
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://db:27017/together')
mongo_client = MongoClient(mongo_uri)

# Initialize models with MongoDB client
relationship_metrics = RelationshipMetrics(mongo_client)

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('authenticate')
def handle_authenticate(data):
    # Verify JWT token
    token = data.get('token')
    if not token:
        emit('authentication_error', {'message': 'No token provided'})
        return
    
    try:
        # Decode token to get user ID
        decoded = decode_token(token)
        user_id = decoded['sub']
        
        # Join a room specific to this user
        join_room(user_id)
        emit('authenticated', {'user_id': user_id})
        print(f"User {user_id} authenticated and joined room")
    except Exception as e:
        emit('authentication_error', {'message': str(e)})

@socketio.on('subscribe_metrics')
def handle_subscribe_metrics(data):
    token = data.get('token')
    partner_id = data.get('partner_id')
    time_window = data.get('time_window', {'minutes': 5})
    
    if not token or not partner_id:
        emit('metrics_error', {'message': 'Missing token or partner_id'})
        return
    
    try:
        # Decode token
        decoded = decode_token(token)
        user_id = decoded['sub']
        
        # Calculate metrics with custom time window
        days = time_window.get('days', 0)
        hours = time_window.get('hours', 0)
        minutes = time_window.get('minutes', 5)
        
        # Default time window is 5 minutes if none provided
        if days == 0 and hours == 0 and minutes == 0:
            minutes = 5
        
        # Calculate metrics
        metrics = relationship_metrics.calculate_metrics(user_id, partner_id, days=days, hours=hours, minutes=minutes)
        
        # Add timestamp
        metrics['timestamp'] = datetime.utcnow().isoformat()
        
        # Send metrics to the client
        emit('metrics_update', metrics, room=user_id)
    except Exception as e:
        emit('metrics_error', {'message': str(e)})

# Function to be called by a background task or webhook when new messages are processed
def notify_metrics_update(user_id, partner_id):
    # Calculate metrics with default window (real-time = last 5 minutes)
    metrics = relationship_metrics.calculate_metrics(user_id, partner_id, minutes=5)
    metrics['timestamp'] = datetime.utcnow().isoformat()
    
    # Send updates to both users
    socketio.emit('metrics_update', metrics, room=user_id)
    socketio.emit('metrics_update', metrics, room=partner_id)