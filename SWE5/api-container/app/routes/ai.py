# api-container/app/routes/ai.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import os

ai_bp = Blueprint('ai', __name__)

# AI service URL from environment variable
AI_URL = os.environ.get('AI_URL', 'http://ai-service:5002/api/ai')

@ai_bp.route('/analyze-message', methods=['POST'])
@jwt_required()
def analyze_message():
    current_user_id = get_jwt_identity()
    data = request.json
    
    response = requests.post(
        f"{AI_URL}/analyze-message", 
        headers={'Authorization': request.headers.get('Authorization')},
        json=data
    )
    
    return jsonify(response.json()), response.status_code

@ai_bp.route('/relationship-metrics/<partner_id>', methods=['GET'])
@jwt_required()
def get_relationship_metrics(partner_id):
    days = request.args.get('days', 30)
    
    response = requests.get(
        f"{AI_URL}/relationship-metrics/{partner_id}?days={days}", 
        headers={'Authorization': request.headers.get('Authorization')}
    )
    
    return jsonify(response.json()), response.status_code

@ai_bp.route('/pet/<partner_id>', methods=['GET'])
@jwt_required()
def get_virtual_pet(partner_id):
    response = requests.get(
        f"{AI_URL}/pet/{partner_id}", 
        headers={'Authorization': request.headers.get('Authorization')}
    )
    
    return jsonify(response.json()), response.status_code

@ai_bp.route('/pet/<partner_id>/feed', methods=['POST'])
@jwt_required()
def feed_pet(partner_id):
    response = requests.post(
        f"{AI_URL}/pet/{partner_id}/feed", 
        headers={'Authorization': request.headers.get('Authorization')}
    )
    
    return jsonify(response.json()), response.status_code

@ai_bp.route('/pet/<partner_id>/play', methods=['POST'])
@jwt_required()
def play_with_pet(partner_id):
    response = requests.post(
        f"{AI_URL}/pet/{partner_id}/play", 
        headers={'Authorization': request.headers.get('Authorization')}
    )
    
    return jsonify(response.json()), response.status_code

@ai_bp.route('/smart-reminders', methods=['GET'])
@jwt_required()
def get_smart_reminders():
    response = requests.get(
        f"{AI_URL}/smart-reminders", 
        headers={'Authorization': request.headers.get('Authorization')}
    )
    
    return jsonify(response.json()), response.status_code