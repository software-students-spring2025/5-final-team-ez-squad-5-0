from werkzeug.security import generate_password_hash
from datetime import datetime
from bson.objectid import ObjectId

def get_user_by_email(mongo, email):
    user = mongo.db.users.find_one({'email': email})
    if user:
        user['_id'] = str(user['_id'])
    return user

def get_user_by_id(mongo, user_id):
    try:
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if user:
            user['_id'] = str(user['_id'])
        return user
    except:
        return None

def create_user(mongo, name, email, password):
    user = {
        'name': name,
        'email': email,
        'password_hash': generate_password_hash(password),
        'created_at': datetime.utcnow()
    }
    
    result = mongo.db.users.insert_one(user)
    user['_id'] = str(result.inserted_id)
    
    return user