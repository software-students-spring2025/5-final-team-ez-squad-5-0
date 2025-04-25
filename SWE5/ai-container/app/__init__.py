# ai-container/app/__init__.py (Updated)
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
import os

# Initialize JWT and Socket.IO
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configure the app
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    
    # Initialize extensions
    jwt.init_app(app)
    socketio.init_app(app, async_mode='eventlet')
    
    # Register blueprints
    from .routes import ai_bp
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    
    @app.route('/')
    def index():
        return 'AI Service for Together App'
    
    return app