from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
import os

# Initialize extensions
mongo = PyMongo()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configure the app
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://db:27017/together')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    
    # Initialize extensions
    mongo.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    from .routes import auth_bp, calendar_bp, messages_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(calendar_bp, url_prefix='/api/calendar')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')
    
    return app

app = create_app()