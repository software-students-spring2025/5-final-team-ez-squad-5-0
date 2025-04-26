from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
import os

# Initialize extensions
mongo = PyMongo()
jwt = JWTManager()

# Minimal hard-coded quiz questions
default_questions = [
    {
        "text": "Would you rather have a cat or a dog?",
        "options": ["Cat", "Dog"],
        "tag": "pets"
    },
    {
        "text": "Would you rather have coffee or tea?",
        "options": ["Coffee", "Tea"],
        "tag": "drinks"
    },
    {
        "text": "Would you rather have sweet or savory breakfast?",
        "options": ["Sweet", "Savory"],
        "tag": "food"
    },
    {
        "text": "Would you rather be a morning person or night owl?",
        "options": ["Morning person", "Night owl"],
        "tag": "lifestyle"
    },
    {
        "text": "Would you rather go to the beach or mountains?",
        "options": ["Beach", "Mountains"],
        "tag": "travel"
    }
]


def initialize_database(app, mongo_instance):
    """Seed default quiz questions if collection is empty"""
    with app.app_context():
        if mongo_instance.db.quiz_questions.count_documents({}) == 0:
            mongo_instance.db.quiz_questions.insert_many(default_questions)
            mongo_instance.db.quiz_questions.create_index("tag")


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configuration
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://db:27017/together')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')

    # Initialize extensions
    mongo.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    from .routes import auth_bp, calendar_bp, messages_bp, daily_question_bp
    from .routes.settings import settings_bp
    from .routes.quiz import quiz_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(calendar_bp, url_prefix='/api/calendar')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    app.register_blueprint(daily_question_bp, url_prefix='/api/daily-question')
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')

    # Seed database
    initialize_database(app, mongo)

    return app


# Create application
app = create_app()
