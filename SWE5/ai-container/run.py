# ai-container/run.py
from app import create_app, socketio
from app.socket_events import *  # Import all socket event handlers

app = create_app()

if __name__ == '__main__':
    # Run the app with Socket.IO
    socketio.run(app, host='0.0.0.0', port=5002, debug=True)