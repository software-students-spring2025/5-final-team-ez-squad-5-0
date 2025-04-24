# web-container/app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-web-secret-key')

# API URL from environment variable
API_URL = os.environ.get('API_URL', 'http://api:5001/api')

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
                flash('Invalid email or password', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        
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
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash(response.json().get('message', 'Registration failed'), 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
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
        flash(f'Error fetching events: {str(e)}', 'error')
    
    # Fetch messages
    try:
        response = api_request('messages/messages', token=session['token'])
        if response.status_code == 200:
            messages = response.json().get('messages', [])
    except Exception as e:
        flash(f'Error fetching messages: {str(e)}', 'error')
    
    return render_template('dashboard.html', user=user, events=events, messages=messages)

# Dashboard question response
@app.route('/dashboard/question', methods=['POST'])
def answer_question():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    response_text = request.form.get('response')
    
    if not response_text:
        flash('Please enter a response to the question', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # In a real app, you would send this to your API
        # For now, just acknowledge receipt
        flash('Your response has been shared', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

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
        flash(f'Error fetching events: {str(e)}', 'error')
    
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
            flash('Event created successfully', 'success')
        else:
            flash(response.json().get('message', 'Failed to create event'), 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('calendar'))

@app.route('/messages')
def messages():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    messages_list = []
    user = session.get('user', {})
    partner_id = None
    partner_name = None
    
    # First get partner info
    try:
        response = api_request('auth/partner/status', token=session['token'])
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'connected' and data.get('partner'):
                partner_id = data['partner'].get('id')
                partner_name = data['partner'].get('name')
    except Exception as e:
        flash(f'Error fetching partner info: {str(e)}', 'error')
    
    # Then get messages
    try:
        response = api_request('messages/messages', token=session['token'])
        if response.status_code == 200:
            messages_list = response.json().get('messages', [])
    except Exception as e:
        flash(f'Error fetching messages: {str(e)}', 'error')
    
    return render_template('messages.html', 
                          messages=messages_list, 
                          user=user,
                          partner_id=partner_id,
                          partner_name=partner_name)

@app.route('/messages/send', methods=['POST'])
def send_message():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    content = request.form.get('content')
    receiver_id = request.form.get('receiver_id')
    
    # Skip sending if no content
    if not content:
        flash('Message content missing', 'error')
        return redirect(url_for('messages'))
    
    try:
        data = {'content': content}
        if receiver_id:
            data['receiverId'] = receiver_id
            
        response = api_request('messages/send', method='POST', token=session['token'], data=data)
        
        if response.status_code == 201:
            flash('Message sent successfully', 'success')
        else:
            error_msg = response.json().get('message', 'Failed to send message')
            flash(f'API Error: {error_msg}', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('messages'))


@app.route('/messages/schedule', methods=['POST'])
def schedule_message():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    content = request.form.get('content')
    receiver_id = request.form.get('receiver_id', 'default-partner-id')
    scheduled_time = request.form.get('scheduled_time')
    
    # Debug info
    print(f"Scheduling message: {content} to {receiver_id} at {scheduled_time}")
    
    # Skip scheduling if no content, receiver, or time
    if not content or not receiver_id or not scheduled_time:
        flash('Message content, recipient, or scheduled time missing', 'error')
        return redirect(url_for('messages'))
    
    try:
        # Call the new API endpoint for scheduling
        response = api_request('messages/schedule', method='POST', token=session['token'], data={
            'content': content,
            'receiverId': receiver_id,
            'scheduledTime': scheduled_time
        })
        
        if response.status_code == 201:
            flash('Message scheduled successfully', 'success')
        else:
            error_msg = response.json().get('message', 'Failed to schedule message')
            flash(f'Error scheduling message: {error_msg}', 'error')
            print(f"API Error: {response.status_code}, {error_msg}")
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        print(f"Exception: {str(e)}")
    
    return redirect(url_for('messages'))

# Add a new route to view scheduled messages
@app.route('/messages/scheduled')
def scheduled_messages():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    scheduled_messages = []
    
    try:
        response = api_request('messages/scheduled', token=session['token'])
        if response.status_code == 200:
            scheduled_messages = response.json().get('scheduled_messages', [])
    except Exception as e:
        flash(f'Error fetching scheduled messages: {str(e)}', 'error')
    
    return render_template('scheduled_messages.html', scheduled_messages=scheduled_messages)

# Add a route to cancel a scheduled message
@app.route('/messages/scheduled/<message_id>/cancel', methods=['POST'])
def cancel_scheduled_message(message_id):
    if 'token' not in session:
        return redirect(url_for('login'))
    
    try:
        response = api_request(f'messages/scheduled/{message_id}/cancel', method='POST', token=session['token'])
        if response.status_code == 200:
            flash('Scheduled message cancelled successfully', 'success')
        else:
            flash(response.json().get('message', 'Failed to cancel scheduled message'), 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('scheduled_messages'))

# Partner routes
@app.route('/partner')
def partner():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    partner_data = {}
    partner_status = 'none'
    
    try:
        response = api_request('auth/partner/status', token=session['token'])
        if response.status_code == 200:
            data = response.json()
            partner_status = data.get('status', 'none')
            partner_data = data.get('partner', {})
    except Exception as e:
        flash(f'Error fetching partner status: {str(e)}', 'error')
    
    return render_template('partner.html', 
                           partner_status=partner_status,
                           partner=partner_data)

@app.route('/partner/send-invite', methods=['POST'])
def send_invite():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    partner_email = request.form.get('partner_email')
    
    if not partner_email:
        flash('Partner email is required', 'error')
        return redirect(url_for('partner'))
    
    try:
        response = api_request('auth/partner/invite', 
                               method='POST',
                               token=session['token'], 
                               data={'partner_email': partner_email})
        
        if response.status_code == 200:
            flash('Partnership invitation sent successfully', 'success')
        else:
            error_msg = response.json().get('message', 'Failed to send invitation')
            flash(error_msg, 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('partner'))

@app.route('/partner/accept-invite', methods=['POST'])
def accept_invite():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    try:
        response = api_request('auth/partner/accept', 
                               method='POST',
                               token=session['token'])
        
        if response.status_code == 200:
            flash('Partnership accepted successfully', 'success')
        else:
            error_msg = response.json().get('message', 'Failed to accept invitation')
            flash(error_msg, 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('partner'))

@app.route('/partner/reject-invite', methods=['POST'])
def reject_invite():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    try:
        response = api_request('auth/partner/reject', 
                               method='POST',
                               token=session['token'])
        
        if response.status_code == 200:
            flash('Partnership invitation rejected', 'success')
        else:
            error_msg = response.json().get('message', 'Failed to reject invitation')
            flash(error_msg, 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('partner'))

@app.route('/partner/cancel-invite', methods=['POST'])
def cancel_invite():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    # This essentially does the same as reject, but from the sender's side
    try:
        response = api_request('auth/partner/reject', 
                               method='POST',
                               token=session['token'])
        
        if response.status_code == 200:
            flash('Partnership invitation canceled', 'success')
        else:
            error_msg = response.json().get('message', 'Failed to cancel invitation')
            flash(error_msg, 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('partner'))

@app.route('/partner/disconnect', methods=['POST'])
def disconnect_partner():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    try:
        # We'll use the same endpoint as reject for simplicity
        response = api_request('auth/partner/reject', 
                               method='POST',
                               token=session['token'])
        
        if response.status_code == 200:
            flash('Partnership disconnected successfully', 'success')
        else:
            error_msg = response.json().get('message', 'Failed to disconnect partnership')
            flash(error_msg, 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('partner'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)