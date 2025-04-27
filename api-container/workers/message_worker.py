# api-container/workers/message_worker.py
import os
import time
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("message_worker")

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://db:27017/together")
client = MongoClient(MONGO_URI)
db = client.get_database()

# Import email utilities - make sure path is correct
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.email_utils import send_partner_message


def get_user_by_id(user_id):
    """
    Retrieve a user by ID
    """
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        return None


def process_scheduled_messages():
    """
    Check for and process scheduled messages that are due to be sent
    """
    current_time = datetime.utcnow()
    logger.info(f"Checking for scheduled messages to send at {current_time}")

    # Find all scheduled messages that are due to be sent
    scheduled_messages = db.scheduled_messages.find(
        {"scheduled_time": {"$lte": current_time}, "status": "pending"}
    )

    count = 0
    for message in scheduled_messages:
        try:
            # Create a new message in the messages collection
            new_message = {
                "content": message["content"],
                "sender_id": message["sender_id"],
                "receiver_id": message["receiver_id"],
                "created_at": current_time,
                "is_read": False,
                "scheduled_from": str(
                    message["_id"]
                ),  # Reference to the original scheduled message
            }

            # Insert the new message
            db.messages.insert_one(new_message)

            # Update the scheduled message status to 'sent'
            db.scheduled_messages.update_one(
                {"_id": message["_id"]},
                {"$set": {"status": "sent", "sent_at": current_time}},
            )

            # Send email notification if receiver has it enabled
            try:
                # Get sender and receiver info
                sender = get_user_by_id(message["sender_id"])
                receiver = get_user_by_id(message["receiver_id"])

                # Check if receiver has email notifications enabled
                if receiver and receiver.get("email_notifications", True):
                    send_partner_message(
                        receiver["email"],
                        sender["name"] if sender else "Your partner",
                        message["content"],
                    )
                    logger.info(f"Sent email notification to {receiver['email']}")
            except Exception as e:
                logger.error(f"Error sending email notification: {str(e)}")
                # Continue processing even if email fails

            count += 1
            logger.info(f"Sent scheduled message {message['_id']}")
        except Exception as e:
            logger.error(f"Error sending scheduled message {message['_id']}: {str(e)}")
            # Mark the message as failed
            db.scheduled_messages.update_one(
                {"_id": message["_id"]}, {"$set": {"status": "failed", "error": str(e)}}
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
