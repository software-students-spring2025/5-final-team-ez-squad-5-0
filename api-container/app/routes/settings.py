from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from .. import mongo
from ..routes import get_user_by_id

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = get_user_by_id(current_user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Remove sensitive fields
    if "password_hash" in user:
        del user["password_hash"]

    return jsonify({"user": user}), 200


@settings_bp.route("/email-notifications", methods=["PUT"])
@jwt_required()
def update_email_notifications():
    current_user_id = get_jwt_identity()
    data = request.json

    enabled = data.get("enabled", True)

    # Update the user's email notification settings
    result = mongo.db.users.update_one(
        {"_id": ObjectId(current_user_id)}, {"$set": {"email_notifications": enabled}}
    )

    if result.modified_count == 0:
        return jsonify({"message": "No changes made"}), 200

    return jsonify({"message": "Email notification settings updated successfully"}), 200


# Register this blueprint in your app/__init__.py file
