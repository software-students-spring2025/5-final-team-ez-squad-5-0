# api-container/workers/message_worker.py
import os
import time
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('message_worker')

# MongoDB connection
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://db:27017/together')
client = MongoClient(MONGO_URI)
db = client.get_database()

def process_scheduled_messages():
    """
    Check for and process scheduled messages that are due to be sent
    """
    current_time = datetime.utcnow()
    logger.info(f"Checking for scheduled messages to send at {current_time}")
    
    # Find all scheduled messages that are due to be sent
    scheduled_messages = db.scheduled_messages.find({
        'scheduled_time': {'$lte': current_time},
        'status': 'pending'
    })
    
    count = 0
    for message in scheduled_messages:
        try:
            # Create a new message in the messages collection
            new_message = {
                'content': message['content'],
                'sender_id': message['sender_id'],
                'receiver_id': message['receiver_id'],
                'created_at': current_time,
                'is_read': False,
                'scheduled_from': str(message['_id'])  # Reference to the original scheduled message
            }
            
            # Insert the new message
            db.messages.insert_one(new_message)
            
            # Update the scheduled message status to 'sent'
            db.scheduled_messages.update_one(
                {'_id': message['_id']},
                {'$set': {'status': 'sent', 'sent_at': current_time}}
            )
            
            count += 1
            logger.info(f"Sent scheduled message {message['_id']}")
        except Exception as e:
            logger.error(f"Error sending scheduled message {message['_id']}: {str(e)}")
            # Mark the message as failed
            db.scheduled_messages.update_one(
                {'_id': message['_id']},
                {'$set': {'status': 'failed', 'error': str(e)}}
            )
    
    logger.info(f"Processed {count} scheduled messages")

def run_worker():
    """
    Run the worker process in a loop
    """
    logger.info("Starting scheduled message worker")
    
    while True:
        try:
            process_scheduled_messages()
        except Exception as e:
            logger.error(f"Error in worker process: {str(e)}")
        
        # Sleep for 60 seconds before the next check
        time.sleep(60)

if __name__ == "__main__":
    run_worker()