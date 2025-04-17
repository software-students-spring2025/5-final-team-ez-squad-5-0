"""
Together Relationship App - API Service
"""
import os
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flasgger import Swagger

# Initialize MongoDB connection
mongo = PyMongo()

# Initialize JWT
jwt = JWTManager()

def create_app(test_config=None):
    """Create and configure Flask application"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
            MONGO_URI=os.environ.get('MONGO_URI', 'mongodb://localhost:27017/together'),
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key'),
            SWAGGER={
                'title': 'Together API',
                'uiversion': 3,
                'description': 'API for Together Relationship Enhancement Platform'
            }
        )
    else:
        app.config.from_mapping(test_config)
    
    # Initialize extensions
    CORS(app)
    mongo.init_app(app)
    jwt.init_app(app)
    Swagger(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.profiles import profile_bp
    from app.routes.messages import message_bp
    from app.routes.activities import activity_bp
    from app.routes.calendar import calendar_bp
    from app.routes.prompts import prompt_bp
    from app.routes.mood import mood_bp
    from app.routes.goals import goal_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profile_bp, url_prefix='/api/profiles')
    app.register_blueprint(message_bp, url_prefix='/api/messages')
    app.register_blueprint(activity_bp, url_prefix='/api/activities')
    app.register_blueprint(calendar_bp, url_prefix='/api/calendar')
    app.register_blueprint(prompt_bp, url_prefix='/api/prompts')
    app.register_blueprint(mood_bp, url_prefix='/api/mood')
    app.register_blueprint(goal_bp, url_prefix='/api/goals')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200
    
    return app