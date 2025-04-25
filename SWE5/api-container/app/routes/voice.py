# api-container/app/routes/voice.py

from flask import Blueprint, request, jsonify
import speech_recognition as sr
import os
import uuid
import datetime

voice_bp = Blueprint('voice', __name__)

UPLOAD_FOLDER = 'uploads/voice'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@voice_bp.route('/api/voice/record', methods=['POST'])
def record_voice():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    
    # Generate unique filename
    filename = f"{uuid.uuid4()}.wav"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    # Save the audio file
    audio_file.save(filepath)
    
    # Transcribe the audio
    text = transcribe_audio(filepath)
    
    # Store in database
    # This will depend on your database schema and setup
    # ...
    
    return jsonify({
        'success': True,
        'transcript': text,
        'audio_path': filepath,
        'timestamp': datetime.datetime.now().isoformat()
    })

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError:
            return "Could not request results from speech recognition service"