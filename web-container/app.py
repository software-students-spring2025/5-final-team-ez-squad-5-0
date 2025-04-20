# web-container/app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-web-secret-key')

# API URL from environment variable
API_URL = os.environ.get('API_URL', 'http://api:5000/api')

# Helper function to make API requests
def api_request(endpoint, method='GET', data=None, token=None):
    url = f"{API_URL}/{endpoint}"
    headers = {}
    
    if token:
        headers['Authorization'] = f"Bearer {token}"
    
    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        headers['Content-Type'] = 'application/json'
        response = requests.post(url, headers=headers, data=json.dumps(data))
    
    return response

# Route for home page
@app.route('/')
def index():
    if 'token' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            response = api_request('auth/login', method='POST', data={
                'email': email,
                'password': password
            })
            
            if response.status_code == 200:
                data = response.json()
                session['token'] = data['token']
                session['user'] = data['user']
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password')
        except Exception as e:
            flash(f'Error: {str(e)}')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('token', None)
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        try:
            response = api_request('auth/register', method='POST', data={
                'name': name,
                'email': email,
                'password': password
            })
            
            if response.status_code == 201:
                flash('Registration successful! Please login.')
                return redirect(url_for('login'))
            else:
                flash(response.json().get('message', 'Registration failed'))
        except Exception as e:
            flash(f'Error: {str(e)}')
    
    return render_template('register.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    user = session.get('user', {})
    events = []
    messages = []
    
    # Fetch events
    try:
        response = api_request('calendar/events', token=session['token'])
        if response.status_code == 200:
            events = response.json().get('events', [])
    except Exception as e:
        flash(f'Error fetching events: {str(e)}')
    
    # Fetch messages
    try:
        response = api_request('messages/messages', token=session['token'])
        if response.status_code == 200:
            messages = response.json().get('messages', [])
    except Exception as e:
        flash(f'Error fetching messages: {str(e)}')
    
    return render_template('dashboard.html', user=user, events=events, messages=messages)

# Calendar routes
@app.route('/calendar')
def calendar():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    events = []
    
    try:
        response = api_request('calendar/events', token=session['token'])
        if response.status_code == 200:
            events = response.json().get('events', [])
    except Exception as e:
        flash(f'Error fetching events: {str(e)}')
    
    return render_template('calendar.html', events=events)

@app.route('/calendar/add', methods=['POST'])
def add_event():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    title = request.form['title']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    
    try:
        response = api_request('calendar/events', method='POST', token=session['token'], data={
            'title': title,
            'startTime': start_time,
            'endTime': end_time
        })
        
        if response.status_code == 201:
            flash('Event created successfully')
        else:
            flash(response.json().get('message', 'Failed to create event'))
    except Exception as e:
        flash(f'Error: {str(e)}')
    
    return redirect(url_for('calendar'))

# Messages routes
@app.route('/messages')
def messages():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    messages_list = []
    
    try:
        response = api_request('messages/messages', token=session['token'])
        if response.status_code == 200:
            messages_list = response.json().get('messages', [])
    except Exception as e:
        flash(f'Error fetching messages: {str(e)}')
    
    return render_template('messages.html', messages=messages_list, user=session.get('user', {}))

@app.route('/messages/send', methods=['POST'])
def send_message():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    content = request.form['content']
    receiver_id = request.form['receiver_id']
    
    try:
        response = api_request('messages/send', method='POST', token=session['token'], data={
            'content': content,
            'receiverId': receiver_id
        })
        
        if response.status_code == 201:
            flash('Message sent successfully')
        else:
            flash(response.json().get('message', 'Failed to send message'))
    except Exception as e:
        flash(f'Error: {str(e)}')
    
    return redirect(url_for('messages'))


@app.route('/messages/schedule', methods=['POST'])
def schedule_message():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    content = request.form['content']
    receiver_id = request.form['receiver_id']
    scheduled_time = request.form['scheduled_time']
    
    try:
        response = api_request('messages/schedule', method='POST', token=session['token'], data={
            'content': content,
            'receiverId': receiver_id,
            'scheduledTime': scheduled_time
        })
        
        if response.status_code == 201:
            flash('Message scheduled successfully')
        else:
            flash(response.json().get('message', 'Failed to schedule message'))
    except Exception as e:
        flash(f'Error: {str(e)}')
    
    return redirect(url_for('messages'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)