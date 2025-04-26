import random
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from .. import mongo

quiz_bp = Blueprint('quiz', __name__)

# Get questions from existing list (simplified version for clarity)
QUIZ_QUESTIONS = [
    { "text": "Would you rather have a cat or a dog?", "options": ["Cat", "Dog"], "tag": "pets" },
    { "text": "Would you rather have coffee or tea?", "options": ["Coffee", "Tea"], "tag": "drinks" },
    { "text": "Sweet or savory breakfast?", "options": ["Sweet", "Savory"], "tag": "food" },
    { "text": "Morning person or night owl?", "options": ["Morning", "Night"], "tag": "lifestyle" },
    { "text": "Beach or mountains?", "options": ["Beach", "Mountains"], "tag": "travel" },
    { "text": "Would you rather summer or winter?", "options": ["Summer", "Winter"], "tag": "season" },
    { "text": "Would you rather pizza or burgers?", "options": ["Pizza", "Burgers"], "tag": "food" },
    { "text": "Would you rather books or movies?", "options": ["Books", "Movies"], "tag": "entertainment" },
    { "text": "Would you rather train or plane?", "options": ["Train", "Plane"], "tag": "travel" },
    { "text": "Would you rather car or bicycle?", "options": ["Car", "Bicycle"], "tag": "transport" },
    { "text": "Would you rather android or ios?", "options": ["Android", "iOS"], "tag": "technology" },
    { "text": "Would you rather pc or mac?", "options": ["PC", "Mac"], "tag": "technology" },
    { "text": "Would you rather chrome or firefox?", "options": ["Chrome", "Firefox"], "tag": "browser" },
    { "text": "Would you rather call or text?", "options": ["Call", "Text"], "tag": "communication" },
    { "text": "Would you rather hug or handshake?", "options": ["Hug", "Handshake"], "tag": "greeting" },
    { "text": "Would you rather board games or video games?", "options": ["Board Games", "Video Games"], "tag": "games" },
    { "text": "Would you rather science or arts?", "options": ["Science", "Arts"], "tag": "subject" },
    { "text": "Would you rather sneakers or sandals?", "options": ["Sneakers", "Sandals"], "tag": "footwear" },
    { "text": "Would you rather black or white?", "options": ["Black", "White"], "tag": "color" },
    { "text": "Would you rather netflix or youtube?", "options": ["Netflix", "YouTube"], "tag": "streaming" },
    { "text": "Would you rather stairs or elevator?", "options": ["Stairs", "Elevator"], "tag": "facility" },
    { "text": "Would you rather bath or shower?", "options": ["Bath", "Shower"], "tag": "hygiene" },
    { "text": "Would you rather pancakes or waffles?", "options": ["Pancakes", "Waffles"], "tag": "breakfast" },
    { "text": "Would you rather tea or juice?", "options": ["Tea", "Juice"], "tag": "drink" },
    { "text": "Would you rather salty or sweet?", "options": ["Salty", "Sweet"], "tag": "taste" },
    { "text": "Would you rather gold or silver?", "options": ["Gold", "Silver"], "tag": "metal" },
    { "text": "Would you rather comedy or drama?", "options": ["Comedy", "Drama"], "tag": "movie" },
    { "text": "Would you rather football or basketball?", "options": ["Football", "Basketball"], "tag": "sports" },
    { "text": "Would you rather pen or pencil?", "options": ["Pen", "Pencil"], "tag": "stationery" },
    { "text": "Would you rather chocolate or vanilla?", "options": ["Chocolate", "Vanilla"], "tag": "flavor" },
    { "text": "Would you rather pool or beach?", "options": ["Pool", "Beach"], "tag": "location" },
    { "text": "Would you rather phone or laptop?", "options": ["Phone", "Laptop"], "tag": "device" },
    { "text": "Would you rather twitter or instagram?", "options": ["Twitter", "Instagram"], "tag": "social" },
    { "text": "Would you rather morning gym or evening gym?", "options": ["Morning Gym", "Evening Gym"], "tag": "exercise" },
    { "text": "Would you rather yoga or pilates?", "options": ["Yoga", "Pilates"], "tag": "exercise" },
    { "text": "Would you rather city or countryside?", "options": ["City", "Countryside"], "tag": "travel" },
    { "text": "Would you rather camping or hotel?", "options": ["Camping", "Hotel"], "tag": "accommodation" },
    { "text": "Would you rather museum or zoo?", "options": ["Museum", "Zoo"], "tag": "place" },
    { "text": "Would you rather sushi or tacos?", "options": ["Sushi", "Tacos"], "tag": "food" },
    { "text": "Would you rather hotdog or burger?", "options": ["Hotdog", "Burger"], "tag": "food" },
    { "text": "Would you rather rain or snow?", "options": ["Rain", "Snow"], "tag": "weather" },
    { "text": "Would you rather sunrise or sunset?", "options": ["Sunrise", "Sunset"], "tag": "time" },
    { "text": "Would you rather rock or pop?", "options": ["Rock", "Pop"], "tag": "music" },
    { "text": "Would you rather classical or hip-hop?", "options": ["Classical", "Hip-hop"], "tag": "music" },
    { "text": "Would you rather e-book or printed book?", "options": ["E-book", "Printed Book"], "tag": "reading" },
    { "text": "Would you rather online shopping or in-store shopping?", "options": ["Online Shopping", "In-store Shopping"], "tag": "shopping" }
]

# Assign unique IDs to each question
for i, q in enumerate(QUIZ_QUESTIONS):
    q['id'] = i + 1

# Get or create an active batch for a user pair
def get_or_create_batch(user_id, partner_id):
    # Sort IDs to ensure consistent pair identification
    pair = sorted([str(user_id), str(partner_id)])
    
    # Check for existing active batch
    batch = mongo.db.quiz_batches.find_one({
        'user1_id': pair[0],
        'user2_id': pair[1],
        'completed': False,
        'expires_at': {'$gt': datetime.utcnow()}
    })
    
    if batch:
        return batch
    
    # Create a new batch with 5 random questions
    questions = random.sample(QUIZ_QUESTIONS, 5)
    
    batch = {
        'user1_id': pair[0],
        'user2_id': pair[1],
        'questions': questions,
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(days=7),
        'completed': False,
        'current_index': 0
    }
    
    result = mongo.db.quiz_batches.insert_one(batch)
    # Retrieve the inserted document to return
    return mongo.db.quiz_batches.find_one({'_id': result.inserted_id})

# Get compatibility score
@quiz_bp.route('/score', methods=['GET'])
@jwt_required()
def get_score():
    uid = get_jwt_identity()
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({'score': 0, 'message': 'No partner connected'}), 200
        
        # Get score from database
        pair = sorted([str(uid), str(partner_id)])
        score_doc = mongo.db.quiz_scores.find_one({'user1_id': pair[0], 'user2_id': pair[1]})
        
        # Count total responses and matches
        total_questions = mongo.db.quiz_responses.count_documents({
            'user_id': uid
        })
        
        # Count matches
        matches = 0
        user_responses = list(mongo.db.quiz_responses.find({'user_id': uid}))
        
        for resp in user_responses:
            partner_resp = mongo.db.quiz_responses.find_one({
                'user_id': partner_id,
                'question_id': resp['question_id']
            })
            
            if partner_resp and partner_resp['answer'] == resp['answer']:
                matches += 1
        
        # Calculate match percentage
        match_percent = 0
        if total_questions > 0:
            partner_responses = mongo.db.quiz_responses.count_documents({
                'user_id': partner_id,
                'question_id': {'$in': [r['question_id'] for r in user_responses]}
            })
            
            if partner_responses > 0:
                match_percent = round((matches / partner_responses) * 100)
        
        return jsonify({
            'score': score_doc['score'] if score_doc else 0,
            'total_answered': total_questions,
            'matches': matches,
            'match_percent': match_percent
        }), 200
        
    except Exception as e:
        current_app.logger.exception("Error fetching score: %s", str(e))
        return jsonify({'score': 0, 'error': str(e)}), 200

# Status endpoint - get current quiz status
@quiz_bp.route('/status', methods=['GET'])
@jwt_required()
def get_status():
    uid = get_jwt_identity()
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({
                'has_partner': False,
                'message': 'No partner connected'
            }), 200
        
        # Get active batch
        pair = sorted([str(uid), str(partner_id)])
        batch = mongo.db.quiz_batches.find_one({
            'user1_id': pair[0],
            'user2_id': pair[1],
            'completed': False
        })
        
        # Check for questions answered by partner but not user
        user_answered = list(mongo.db.quiz_responses.distinct('question_id', {
            'user_id': uid
        }))
        
        partner_answered = list(mongo.db.quiz_responses.distinct('question_id', {
            'user_id': partner_id
        }))
        
        pending_questions = [q for q in partner_answered if q not in user_answered]
        
        # Get compatibility score
        score_doc = mongo.db.quiz_scores.find_one({'user1_id': pair[0], 'user2_id': pair[1]})
        
        return jsonify({
            'has_partner': True,
            'partner_name': user.get('partner_name', 'Partner'),
            'current_score': score_doc['score'] if score_doc else 0,
            'has_active_batch': batch is not None,
            'pending_questions': len(pending_questions),
            'batch_info': {
                'id': str(batch['_id']) if batch else None,
                'progress': f"{batch['current_index']}/{len(batch['questions'])}" if batch else "0/0",
                'completed': batch['completed'] if batch else False
            } if batch else None
        }), 200
    except Exception as e:
        current_app.logger.exception("Error fetching status: %s", str(e))
        return jsonify({'error': str(e)}), 500

# Batch endpoints
@quiz_bp.route('/batch', methods=['GET'])
@jwt_required()
def get_batch():
    uid = get_jwt_identity()
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({'error': 'No partner connected'}), 400
        
        # Get or create batch
        batch = get_or_create_batch(uid, partner_id)
        
        return jsonify({
            'batch_id': str(batch['_id']),
            'total_questions': len(batch['questions']),
            'current_index': batch['current_index'],
            'completed': batch['completed'],
            'expires_at': batch['expires_at'].isoformat()
        }), 200
    except Exception as e:
        current_app.logger.exception("Error getting batch: %s", str(e))
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/batch/new', methods=['POST'])
@jwt_required()
def create_new_batch():
    uid = get_jwt_identity()
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({'error': 'No partner connected'}), 400
        
        # Mark existing batches as completed
        pair = sorted([str(uid), str(partner_id)])
        mongo.db.quiz_batches.update_many(
            {'user1_id': pair[0], 'user2_id': pair[1], 'completed': False},
            {'$set': {'completed': True}}
        )
        
        # Create new batch
        batch = get_or_create_batch(uid, partner_id)
        
        return jsonify({
            'message': 'New batch created',
            'batch_id': str(batch['_id']),
            'total_questions': len(batch['questions'])
        }), 200
    except Exception as e:
        current_app.logger.exception("Error creating batch: %s", str(e))
        return jsonify({'error': str(e)}), 500

# Get current question
@quiz_bp.route('/question', methods=['GET'])
@jwt_required()
def get_question():
    uid = get_jwt_identity()
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({'error': 'No partner connected'}), 400
        
        # Get active batch
        batch = get_or_create_batch(uid, partner_id)
        
        # Check if batch is complete
        if batch['current_index'] >= len(batch['questions']):
            mongo.db.quiz_batches.update_one(
                {'_id': batch['_id']},
                {'$set': {'completed': True}}
            )
            return jsonify({'message': 'Batch completed', 'completed': True}), 200
        
        # Get current question
        current_q = batch['questions'][batch['current_index']]
        
        # Check if user has already answered this question
        existing_answer = mongo.db.quiz_responses.find_one({
            'user_id': uid,
            'question_id': current_q['id']
        })
        
        if existing_answer:
            # Move to next question if already answered
            mongo.db.quiz_batches.update_one(
                {'_id': batch['_id']},
                {'$inc': {'current_index': 1}}
            )
            # Recursive call to get next question
            return get_question()
        
        # Return the current question
        return jsonify({
            'id': current_q['id'],
            'question': current_q['text'],
            'options': current_q['options'],
            'batch_progress': {
                'current': batch['current_index'] + 1,
                'total': len(batch['questions'])
            }
        }), 200
    except Exception as e:
        current_app.logger.exception("Error getting question: %s", str(e))
        return jsonify({'error': str(e)}), 500

# Submit answer
@quiz_bp.route('/answer', methods=['POST'])
@jwt_required()
def submit_answer():
    uid = get_jwt_identity()
    data = request.json or {}
    
    question_id = data.get('question_id')
    answer = data.get('answer')
    
    if not question_id or answer is None:
        return jsonify({'message': 'question_id and answer required'}), 400
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({'error': 'No partner connected'}), 400
        
        # Get active batch
        pair = sorted([str(uid), str(partner_id)])
        batch = mongo.db.quiz_batches.find_one({
            'user1_id': pair[0],
            'user2_id': pair[1],
            'completed': False
        })
        
        if not batch:
            return jsonify({'error': 'No active question batch'}), 400
        
        # Save response
        mongo.db.quiz_responses.insert_one({
            'user_id': uid,
            'question_id': question_id,
            'answer': answer,
            'created_at': datetime.utcnow(),
            'batch_id': str(batch['_id'])
        })
        
        # Check if partner has answered
        partner_resp = mongo.db.quiz_responses.find_one({
            'user_id': partner_id,
            'question_id': question_id
        })
        
        # Initialize response data
        response_data = {
            'message': 'Answer submitted',
            'waiting_for_partner': True,
            'delta': 0,
            'is_match': False,
            'new_score': None,
            'batch_complete': False
        }
        
        # If partner has answered this question
        if partner_resp:
            is_match = partner_resp['answer'] == answer
            delta = 5 if is_match else -2
            
            # Update response data
            response_data['waiting_for_partner'] = False
            response_data['is_match'] = is_match
            response_data['delta'] = delta
            
            # Update compatibility score
            score_doc = mongo.db.quiz_scores.find_one({'user1_id': pair[0], 'user2_id': pair[1]})
            
            if score_doc:
                new_score = max(0, score_doc['score'] + delta)
                mongo.db.quiz_scores.update_one(
                    {'user1_id': pair[0], 'user2_id': pair[1]},
                    {'$set': {'score': new_score}}
                )
            else:
                new_score = max(0, delta)
                mongo.db.quiz_scores.insert_one({
                    'user1_id': pair[0],
                    'user2_id': pair[1],
                    'score': new_score
                })
            
            response_data['new_score'] = new_score
            
            # Move to next question in batch
            mongo.db.quiz_batches.update_one(
                {'_id': batch['_id']},
                {'$inc': {'current_index': 1}}
            )
            
            # Check if batch is complete
            updated_batch = mongo.db.quiz_batches.find_one({'_id': batch['_id']})
            if updated_batch['current_index'] >= len(batch['questions']):
                mongo.db.quiz_batches.update_one(
                    {'_id': batch['_id']},
                    {'$set': {'completed': True}}
                )
                response_data['batch_complete'] = True
        
        return jsonify(response_data), 200
    except Exception as e:
        current_app.logger.exception("Error submitting answer: %s", str(e))
        return jsonify({'error': str(e)}), 500

# Get batch results (for review at end of batch)
@quiz_bp.route('/batch/<batch_id>/results', methods=['GET'])
@jwt_required()
def get_batch_results(batch_id):
    uid = get_jwt_identity()
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({'error': 'No partner connected'}), 400
        
        # Get the batch
        batch = mongo.db.quiz_batches.find_one({'_id': ObjectId(batch_id)})
        
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404
        
        # Get answers for this batch
        user_responses = list(mongo.db.quiz_responses.find({
            'user_id': uid,
            'batch_id': batch_id
        }))
        
        partner_responses = list(mongo.db.quiz_responses.find({
            'user_id': partner_id,
            'batch_id': batch_id
        }))
        
        # Format results
        results = []
        
        for q in batch['questions']:
            user_answer = next((r['answer'] for r in user_responses if r['question_id'] == q['id']), None)
            partner_answer = next((r['answer'] for r in partner_responses if r['question_id'] == q['id']), None)
            
            if user_answer is not None and partner_answer is not None:
                results.append({
                    'question': q['text'],
                    'your_answer': user_answer,
                    'partner_answer': partner_answer,
                    'match': user_answer == partner_answer
                })
        
        return jsonify({'questions': results}), 200
    except Exception as e:
        current_app.logger.exception("Error getting batch results: %s", str(e))
        return jsonify({'error': str(e)}), 500

# Legacy endpoints to maintain backward compatibility
@quiz_bp.route('/question/<int:question_id>', methods=['GET'])
@jwt_required()
def get_question_by_id(question_id):
    # Return a random question for compatibility
    q = random.choice(QUIZ_QUESTIONS)
    return jsonify({
        'id': question_id,
        'question': q['text'],
        'options': q['options']
    }), 200

# Add this endpoint to your quiz.py file

@quiz_bp.route('/check-partner-response', methods=['GET'])
@jwt_required()
def check_partner_response():
    uid = get_jwt_identity()
    question_id = request.args.get('question_id')
    
    if not question_id:
        return jsonify({'error': 'question_id is required'}), 400
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({'error': 'No partner connected'}), 400
        
        # Check if partner has answered this question
        partner_resp = mongo.db.quiz_responses.find_one({
            'user_id': partner_id,
            'question_id': int(question_id)
        })
        
        if not partner_resp:
            # Partner hasn't answered yet
            return jsonify({
                'has_answered': False
            }), 200
        
        # Partner has answered, check if user has answered too
        user_resp = mongo.db.quiz_responses.find_one({
            'user_id': uid,
            'question_id': int(question_id)
        })
        
        if not user_resp:
            # User hasn't answered yet (unusual case)
            return jsonify({
                'has_answered': False
            }), 200
        
        # Both have answered, check for match
        is_match = partner_resp['answer'] == user_resp['answer']
        delta = 5 if is_match else -2
        
        # Get active batch
        pair = sorted([str(uid), str(partner_id)])
        batch = mongo.db.quiz_batches.find_one({
            'user1_id': pair[0],
            'user2_id': pair[1],
            'completed': False
        })
        
        # Get or update score
        score_doc = mongo.db.quiz_scores.find_one({'user1_id': pair[0], 'user2_id': pair[1]})
        new_score = None
        
        if score_doc:
            new_score = score_doc['score']
        
        # Check if batch is complete
        batch_complete = False
        if batch:
            current_index = batch.get('current_index', 0)
            total_questions = len(batch.get('questions', []))
            batch_complete = current_index >= total_questions
        
        return jsonify({
            'has_answered': True,
            'is_match': is_match,
            'delta': delta,
            'new_score': new_score,
            'batch_complete': batch_complete
        }), 200
        
    except Exception as e:
        current_app.logger.exception("Error checking partner response: %s", str(e))
        return jsonify({'error': str(e)}), 500