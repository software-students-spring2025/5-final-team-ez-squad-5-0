from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson.objectid import ObjectId
import random
import pytz

from .. import mongo
from ..email_utils import send_invitation_email, send_partner_message

auth_bp = Blueprint("auth", __name__)
calendar_bp = Blueprint("calendar", __name__)
messages_bp = Blueprint("messages_bp", __name__)
daily_question_bp = Blueprint("daily_question", __name__)


# Helper functions
def get_user_by_email(email):
    user = mongo.db.users.find_one({"email": email})
    if user:
        user["_id"] = str(user["_id"])
    return user


def get_user_by_id(user_id):
    try:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except:
        return None


def create_user(name, email, password, partner_email=None):
    user = {
        "name": name,
        "email": email,
        "password_hash": generate_password_hash(password),
        "email_notifications": True,  # Enable by default
        "created_at": datetime.utcnow(),
    }

    # Add partner email if provided
    if partner_email:
        user["partner_email"] = partner_email

    result = mongo.db.users.insert_one(user)
    user["_id"] = str(result.inserted_id)

    # If partner email is provided, check if partner exists and link them
    if partner_email:
        partner = get_user_by_email(partner_email)
        if partner:
            # Link the users as partners
            partner_id = partner["_id"]
            user_id = user["_id"]

            # Update the new user with partner's ID and status
            mongo.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"partner_id": partner_id, "partner_status": "pending_sent"}},
            )

            # Update the partner with the new user's ID and status
            mongo.db.users.update_one(
                {"_id": ObjectId(partner_id)},
                {"$set": {"partner_id": user_id, "partner_status": "pending_received"}},
            )

    return user


# Authentication routes
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    # Check if email already exists
    if get_user_by_email(data["email"]):
        return jsonify({"message": "Email already registered"}), 400

    # Get partner email if provided
    partner_email = data.get("partner_email")

    # Create new user
    user = create_user(data["name"], data["email"], data["password"], partner_email)

    # If partner email is provided and partner doesn't exist yet, send invitation
    if partner_email and not get_user_by_email(partner_email):
        try:
            send_invitation_email(partner_email, data["name"])
        except Exception as e:
            # Log error but don't prevent registration
            print(f"Error sending invitation email: {e}")

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    user = get_user_by_email(data["email"])

    if not user or not check_password_hash(user["password_hash"], data["password"]):
        return jsonify({"message": "Invalid email or password"}), 401

    # Create access token
    access_token = create_access_token(identity=str(user["_id"]))

    return (
        jsonify({"message": "Login successful", "token": access_token, "user": user}),
        200,
    )


@auth_bp.route("/notifications/email", methods=["PUT"])
@jwt_required()
def update_email_notifications():
    current_user_id = get_jwt_identity()
    data = request.json

    enabled = data.get("enabled", True)

    result = mongo.db.users.update_one(
        {"_id": ObjectId(current_user_id)}, {"$set": {"email_notifications": enabled}}
    )

    if result.modified_count == 0:
        return jsonify({"message": "No changes made"}), 200

    return (
        jsonify({"message": "Email notification preferences updated successfully"}),
        200,
    )


# Calendar routes
@calendar_bp.route("/events", methods=["GET"])
@jwt_required()
def get_events():
    current_user_id = get_jwt_identity()

    # Get user to check for partner
    current_user = get_user_by_id(current_user_id)

    # Query for events created by the current user
    query = {"user_id": current_user_id}

    # If user has a connected partner, include their events too
    if (
        current_user.get("partner_id")
        and current_user.get("partner_status") == "connected"
    ):
        query = {
            "$or": [
                {"user_id": current_user_id},
                {"user_id": current_user.get("partner_id")},
            ]
        }

    events = list(mongo.db.events.find(query).sort("start_time", 1))
    for event in events:
        event["_id"] = str(event["_id"])

        # Add creator info
        if event["user_id"] == current_user_id:
            event["creator"] = "you"
        else:
            event["creator"] = "partner"

    return jsonify({"events": events}), 200


@calendar_bp.route("/events", methods=["POST"])
@jwt_required()
def create_event():
    current_user_id = get_jwt_identity()
    data = request.json

    try:
        local_tz = pytz.timezone("America/New_York")

        local_start = datetime.fromisoformat(data["startTime"])
        local_end = datetime.fromisoformat(data["endTime"])

        start_utc = local_tz.localize(local_start).astimezone(pytz.utc)
        end_utc = local_tz.localize(local_end).astimezone(pytz.utc)
    except Exception as e:
        return jsonify({"message": f"Invalid date format: {str(e)}"}), 400

    event = {
        "title": data["title"],
        "description": data.get("description", ""),
        "start_time": start_utc,
        "end_time": end_utc,
        "user_id": current_user_id,
        "created_at": datetime.utcnow(),
    }

    result = mongo.db.events.insert_one(event)
    event["_id"] = str(result.inserted_id)

    return jsonify({"message": "Event created successfully", "event": event}), 201


# Messages routes
@messages_bp.route("/messages", methods=["GET"])
@jwt_required()
def get_messages():
    current_user_id = get_jwt_identity()

    messages = list(
        mongo.db.messages.find(
            {"$or": [{"sender_id": current_user_id}, {"receiver_id": current_user_id}]}
        ).sort("created_at", -1)
    )

    for message in messages:
        message["_id"] = str(message["_id"])

    return jsonify({"messages": messages}), 200


@messages_bp.route("/send", methods=["POST"])
@jwt_required()
def send_message():
    current_user_id = get_jwt_identity()
    data = request.json

    # Get current user
    current_user = get_user_by_id(current_user_id)

    # Use provided receiver_id or default to partner
    receiver_id = data.get("receiverId")

    # If no receiver_id provided, check if user has partner
    if not receiver_id:
        if (
            current_user.get("partner_id")
            and current_user.get("partner_status") == "connected"
        ):
            receiver_id = current_user.get("partner_id")
        else:
            return (
                jsonify({"message": "No partner connected and no receiver specified"}),
                400,
            )

    # Get receiver information for email notification
    receiver = get_user_by_id(receiver_id)
    if not receiver:
        return jsonify({"message": "Receiver not found"}), 404

    message = {
        "content": data["content"],
        "sender_id": current_user_id,
        "receiver_id": receiver_id,
        "created_at": datetime.utcnow(),
        "is_read": False,
    }

    result = mongo.db.messages.insert_one(message)
    message["_id"] = str(result.inserted_id)

    # Send email notification if the receiver has it enabled
    if receiver.get("email_notifications", True):
        try:
            send_partner_message(
                receiver["email"], current_user["name"], data["content"]
            )
        except Exception as e:
            # Log error but don't prevent message sending
            print(f"Error sending email notification: {e}")

    return jsonify({"message": "Message sent successfully", "data": message}), 201

@messages_bp.route("/schedule", methods=["POST"])
@jwt_required()
def schedule_message():
    current_user_id = get_jwt_identity()
    data = request.json

    try:
        local_tz = pytz.timezone("America/New_York")
        local_scheduled = datetime.fromisoformat(data["scheduledTime"])
        scheduled_time = local_tz.localize(local_scheduled).astimezone(pytz.utc)
    except Exception as e:
        return jsonify({"message": f"Invalid date format: {str(e)}"}), 400

    scheduled_message = {
        "content": data["content"],
        "sender_id": current_user_id,
        "receiver_id": data["receiverId"],
        "scheduled_time": scheduled_time,
        "created_at": datetime.utcnow(),
        "status": "pending",
    }

    result = mongo.db.scheduled_messages.insert_one(scheduled_message)
    scheduled_message["_id"] = str(result.inserted_id)

    return (
        jsonify(
            {"message": "Message scheduled successfully", "data": scheduled_message}
        ),
        201,
    )


@messages_bp.route("/scheduled", methods=["GET"])
@jwt_required()
def get_scheduled_messages():
    current_user_id = get_jwt_identity()

    # Get all scheduled messages for the current user
    scheduled_messages = list(
        mongo.db.scheduled_messages.find(
            {"sender_id": current_user_id, "status": "pending"}
        ).sort("scheduled_time", 1)
    )

    for message in scheduled_messages:
        message["_id"] = str(message["_id"])
        # Convert datetime objects to strings for JSON serialization
        message["scheduled_time"] = message["scheduled_time"].isoformat()
        message["created_at"] = message["created_at"].isoformat()

    return jsonify({"scheduled_messages": scheduled_messages}), 200


@messages_bp.route("/scheduled/<message_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_scheduled_message(message_id):
    current_user_id = get_jwt_identity()

    try:
        # Find and update the message to set status to 'cancelled'
        result = mongo.db.scheduled_messages.update_one(
            {
                "_id": ObjectId(message_id),
                "sender_id": current_user_id,
                "status": "pending",
            },
            {"$set": {"status": "cancelled"}},
        )

        if result.modified_count == 0:
            return jsonify({"message": "No pending message found with that ID"}), 404

        return jsonify({"message": "Scheduled message cancelled successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


# Partner relationship endpoints
@auth_bp.route("/partner/invite", methods=["POST"])
@jwt_required()
def invite_partner():
    current_user_id = get_jwt_identity()
    data = request.json
    partner_email = data.get("partner_email")

    # Get current user info
    current_user = get_user_by_id(current_user_id)
    if not current_user:
        return jsonify({"message": "User not found"}), 404

    # Check if partner exists
    partner = get_user_by_email(partner_email)

    # Check if user already has a partner
    if (
        current_user.get("partner_id")
        and current_user.get("partner_status") == "connected"
    ):
        return jsonify({"message": "You are already connected with a partner"}), 400

    # Check if partner already has a different partner
    if (
        partner
        and partner.get("partner_id")
        and partner.get("partner_id") != current_user_id
        and partner.get("partner_status") == "connected"
    ):
        return (
            jsonify({"message": "This user is already connected with another partner"}),
            400,
        )

    # If partner exists in the system
    if partner:
        # Update current user with pending partnership
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user_id)},
            {"$set": {"partner_id": partner["_id"], "partner_status": "pending_sent"}},
        )

        # Update partner with pending invitation
        mongo.db.users.update_one(
            {"_id": ObjectId(partner["_id"])},
            {
                "$set": {
                    "partner_id": current_user_id,
                    "partner_status": "pending_received",
                }
            },
        )

        # Send email notification to partner
        if partner.get("email_notifications", True):
            try:
                send_partner_message(
                    partner["email"],
                    current_user["name"],
                    f"{current_user['name']} has invited you to connect on Together. Log in to accept or decline this invitation.",
                )
            except Exception as e:
                print(f"Error sending partnership email: {e}")
    else:
        # Partner doesn't exist in the system, send invitation email
        try:
            send_invitation_email(partner_email, current_user["name"])

            # Update current user with pending partnership
            mongo.db.users.update_one(
                {"_id": ObjectId(current_user_id)},
                {"$set": {"partner_email": partner_email, "partner_status": "invited"}},
            )
        except Exception as e:
            print(f"Error sending invitation email: {e}")
            return jsonify({"message": "Error sending invitation"}), 500

    return jsonify({"message": "Partnership invitation sent successfully"}), 200


@auth_bp.route("/partner/accept", methods=["POST"])
@jwt_required()
def accept_partner():
    current_user_id = get_jwt_identity()

    # Check if user has a pending invitation
    current_user = get_user_by_id(current_user_id)
    if (
        not current_user.get("partner_id")
        or current_user.get("partner_status") != "pending_received"
    ):
        return jsonify({"message": "No pending partnership invitation found"}), 404

    partner_id = current_user.get("partner_id")
    partner = get_user_by_id(partner_id)

    # Update both users to connected status
    mongo.db.users.update_one(
        {"_id": ObjectId(current_user_id)}, {"$set": {"partner_status": "connected"}}
    )

    mongo.db.users.update_one(
        {"_id": ObjectId(partner_id)}, {"$set": {"partner_status": "connected"}}
    )

    # Send notification email to partner about acceptance
    if partner and partner.get("email_notifications", True):
        try:
            send_partner_message(
                partner["email"],
                current_user["name"],
                f"{current_user['name']} has accepted your partnership invitation. You are now connected!",
            )
        except Exception as e:
            print(f"Error sending acceptance email: {e}")

    return jsonify({"message": "Partnership accepted successfully"}), 200


@auth_bp.route("/partner/reject", methods=["POST"])
@jwt_required()
def reject_partner():
    current_user_id = get_jwt_identity()

    # Check if user has a pending invitation
    current_user = get_user_by_id(current_user_id)
    if not current_user.get("partner_id"):
        return jsonify({"message": "No partnership data found"}), 404

    partner_id = current_user.get("partner_id")
    partner = get_user_by_id(partner_id)

    # Remove partnership data from both users
    mongo.db.users.update_one(
        {"_id": ObjectId(current_user_id)},
        {"$unset": {"partner_id": "", "partner_status": ""}},
    )

    mongo.db.users.update_one(
        {"_id": ObjectId(partner_id)},
        {"$unset": {"partner_id": "", "partner_status": ""}},
    )

    # Notify partner about rejection (optional)
    if partner and partner.get("email_notifications", True):
        try:
            send_partner_message(
                partner["email"],
                "Together App",
                f"Your partnership invitation has been declined.",
            )
        except Exception as e:
            print(f"Error sending rejection email: {e}")

    return jsonify({"message": "Partnership removed"}), 200


@auth_bp.route("/partner/status", methods=["GET"])
@jwt_required()
def get_partner_status():
    current_user_id = get_jwt_identity()

    # Get current user with partner info
    current_user = get_user_by_id(current_user_id)

    partner_data = None
    if current_user.get("partner_id"):
        partner = get_user_by_id(current_user.get("partner_id"))
        if partner:
            partner_data = {
                "id": partner["_id"],
                "name": partner["name"],
                "email": partner["email"],
            }

    return (
        jsonify(
            {
                "has_partner": bool(current_user.get("partner_id")),
                "status": current_user.get("partner_status", "none"),
                "partner": partner_data,
            }
        ),
        200,
    )


# Add to api-container/app/routes/__init__.py or create a new file


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    data = request.json

    name = data.get("name")
    if not name:
        return jsonify({"message": "Name is required"}), 400

    result = mongo.db.users.update_one(
        {"_id": ObjectId(current_user_id)}, {"$set": {"name": name}}
    )

    if result.modified_count == 0:
        return jsonify({"message": "No changes made"}), 200

    return jsonify({"message": "Profile updated successfully"}), 200


@auth_bp.route("/password", methods=["PUT"])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    data = request.json

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({"message": "Both current and new password are required"}), 400

    # Get current user
    user = mongo.db.users.find_one({"_id": ObjectId(current_user_id)})
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Verify current password
    if not check_password_hash(user["password_hash"], current_password):
        return jsonify({"message": "Current password is incorrect"}), 401

    # Update with new password
    new_password_hash = generate_password_hash(new_password)
    result = mongo.db.users.update_one(
        {"_id": ObjectId(current_user_id)},
        {"$set": {"password_hash": new_password_hash}},
    )

    if result.modified_count == 0:
        return jsonify({"message": "No changes made"}), 200

    return jsonify({"message": "Password updated successfully"}), 200



@daily_question_bp.route("/", methods=["GET"])
@jwt_required()
def get_daily_question():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    question_doc = mongo.db.daily_questions.find_one({"date": today})

    if question_doc:
        return jsonify({"question": question_doc["question"]}), 200
    else:
        # List of fallback questions
        questions = [
            "What made you smile today?",
            "What's one thing you appreciate about your partner?",
            "What's your goal for today?",
            "Share a happy memory!",
            "What's one thing you're grateful for today?",
        ]
        import random

        random_question = random.choice(questions)
        mongo.db.daily_questions.insert_one(
            {"date": today, "question": random_question, "answers": []}
        )
        return jsonify({"question": random_question}), 200


@daily_question_bp.route("/answers", methods=["GET"])
@jwt_required()
def get_daily_answers():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    question_doc = mongo.db.daily_questions.find_one({"date": today})

    if not question_doc:
        return jsonify({"answers": []}), 200

    return jsonify({"answers": question_doc.get("answers", [])}), 200


@daily_question_bp.route("/answer", methods=["POST"])
@jwt_required()
def submit_answer():
    data = request.json
    user_id = get_jwt_identity()

    if not data.get("answer"):
        return jsonify({"message": "Answer is required"}), 400

    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    today = datetime.utcnow().strftime("%Y-%m-%d")

    mongo.db.daily_questions.update_one(
        {"date": today},
        {
            "$push": {
                "answers": {
                    "user_id": user_id,
                    "user_name": user.get("name", "Anonymous"),
                    "answer": data["answer"],
                }
            }
        },
        upsert=True,  # Create if it doesn't exist
    )

    return jsonify({"message": "Answer submitted successfully"}), 200
