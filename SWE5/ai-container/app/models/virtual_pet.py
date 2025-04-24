# ai-container/app/models/virtual_pet.py
from datetime import datetime, timedelta
import random

class VirtualPet:
    def __init__(self, mongo_client):
        self.db = mongo_client.get_database()
    
    def get_pet(self, user_id, partner_id):
        """Get or create a virtual pet for the relationship"""
        # Find pair ID (consistent regardless of user/partner order)
        pair_id = '_'.join(sorted([user_id, partner_id]))
        
        # Try to get existing pet
        pet = self.db.virtual_pets.find_one({'pair_id': pair_id})
        
        if not pet:
            # Create new pet
            pet = {
                'pair_id': pair_id,
                'name': 'Lovey',  # Default name, users can change
                'species': random.choice(['cat', 'dog', 'bird', 'rabbit']),
                'happiness': 50,
                'health': 50,
                'last_fed': datetime.utcnow(),
                'last_played': datetime.utcnow(),
                'created_at': datetime.utcnow(),
                'level': 1,
                'experience': 0
            }
            
            self.db.virtual_pets.insert_one(pet)
            pet['_id'] = str(pet['_id'])
        else:
            pet['_id'] = str(pet['_id'])
        
        return pet
    
    def update_pet_state(self, user_id, partner_id):
        """Update pet state based on relationship activity"""
        pair_id = '_'.join(sorted([user_id, partner_id]))
        pet = self.db.virtual_pets.find_one({'pair_id': pair_id})
        
        if not pet:
            return self.get_pet(user_id, partner_id)
        
        # Get recent messages (last 7 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        messages = list(self.db.messages.find({
            '$or': [
                {'sender_id': user_id, 'receiver_id': partner_id},
                {'sender_id': partner_id, 'receiver_id': user_id}
            ],
            'created_at': {'$gte': start_date, '$lte': end_date}
        }))
        
        # Calculate new happiness level
        message_count = len(messages)
        
        # Decrease happiness if not fed or played with
        time_since_fed = (datetime.utcnow() - pet['last_fed']).total_seconds() / 3600  # hours
        time_since_played = (datetime.utcnow() - pet['last_played']).total_seconds() / 3600  # hours
        
        happiness = pet['happiness']
        health = pet['health']
        
        # Messages improve happiness
        if message_count > 20:
            happiness += 10
        elif message_count > 10:
            happiness += 5
        elif message_count > 5:
            happiness += 2
        
        # Lack of interaction decreases happiness
        if time_since_fed > 24:
            happiness -= 5
            health -= 3
        
        if time_since_played > 48:
            happiness -= 3
        
        # Cap values
        happiness = max(0, min(100, happiness))
        health = max(0, min(100, health))
        
        # Update experience and level
        experience = pet['experience'] + message_count
        level = 1 + (experience // 100)  # Level up every 100 experience points
        
        # Update pet in database
        self.db.virtual_pets.update_one(
            {'_id': pet['_id']},
            {'$set': {
                'happiness': happiness,
                'health': health,
                'experience': experience,
                'level': level
            }}
        )
        
        pet.update({
            'happiness': happiness,
            'health': health,
            'experience': experience,
            'level': level
        })
        
        return pet
    
    def feed_pet(self, user_id, partner_id):
        """Feed the virtual pet"""
        pair_id = '_'.join(sorted([user_id, partner_id]))
        pet = self.db.virtual_pets.find_one({'pair_id': pair_id})
        
        if not pet:
            return self.get_pet(user_id, partner_id)
        
        # Update last_fed time and increase health
        new_health = min(100, pet['health'] + 10)
        new_happiness = min(100, pet['happiness'] + 5)
        
        self.db.virtual_pets.update_one(
            {'_id': pet['_id']},
            {'$set': {
                'last_fed': datetime.utcnow(),
                'health': new_health,
                'happiness': new_happiness
            }}
        )
        
        pet.update({
            'last_fed': datetime.utcnow(),
            'health': new_health,
            'happiness': new_happiness
        })
        
        return pet
    
    def play_with_pet(self, user_id, partner_id):
        """Play with the virtual pet"""
        pair_id = '_'.join(sorted([user_id, partner_id]))
        pet = self.db.virtual_pets.find_one({'pair_id': pair_id})
        
        if not pet:
            return self.get_pet(user_id, partner_id)
        
        # Update last_played time and increase happiness
        new_happiness = min(100, pet['happiness'] + 15)
        
        self.db.virtual_pets.update_one(
            {'_id': pet['_id']},
            {'$set': {
                'last_played': datetime.utcnow(),
                'happiness': new_happiness
            }}
        )
        
        pet.update({
            'last_played': datetime.utcnow(),
            'happiness': new_happiness
        })
        
        return pet