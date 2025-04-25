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
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'together@example.com')
    
    # Initialize extensions
    mongo.init_app(app)
    jwt.init_app(app)
    
    # Initialize email
    from .email_utils import mail, init_mail
    init_mail(app)
    
    # Register blueprints
    from .routes import auth_bp, calendar_bp, messages_bp
    from .routes.settings import settings_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(calendar_bp, url_prefix='/api/calendar')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    
    return app

app = create_app()