"""
Home/Dashboard component for the Together web application
"""
import os
import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import altair as alt

# API URL
API_URL = os.environ.get('API_URL', 'http://localhost:5000')

def display_home():
    """Display the home dashboard"""
    st.title("Dashboard")
    
    # Display welcome message
    now = datetime.now()
    hour = now.hour
    
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    st.markdown(f"## {greeting}, {st.session_state.user['name']}!")
    
    # Show partner connection state
    if not st.session_state.partner:
        display_partner_invitation()
    else:
        # Display partner mood
        display_mood_summary()
    
    # Create dashboard columns
    col1, col2 = st.columns(2)
    
    with col1:
        display_upcoming_events()
        display_daily_prompt()
    
    with col2:
        display_recent_messages()
        display_activity_suggestions()

def display_partner_invitation():
    """Display partner invitation section"""
    st.markdown("### Connect with your partner")
    st.markdown("Invite your partner to join you on Together to unlock the full experience.")
    
    with st.form("invite_partner_form"):
        partner_email = st.text_input("Partner's Email")
        submit = st.form_submit_button("Send Invitation")
        
        if submit:
            if not partner_email:
                st.error("Please enter your partner's email")
                return
            
            try:
                response = requests.post(
                    f"{API_URL}/api/auth/invite-partner",
                    headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                    json={"partner_email": partner_email}
                )
                
                if response.status_code == 200:
                    st.success("Invitation sent successfully!")
                    st.session_state.user['partner_status'] = 'invited'
                    st.experimental_rerun()
                else:
                    st.error(response.json().get("error", "Failed to send invitation. Please try again."))
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

def display_mood_summary():
    """Display mood summary for user and partner"""
    st.markdown("### Today's Mood")
    
    try:
        response = requests.get(
            f"{API_URL}/api/mood/today",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        
        if response.status_code == 200:
            mood_data = response.json()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### Your Mood")
                
                if mood_data.get('user'):
                    user_mood = mood_data['user']
                    display_mood_card(user_mood, is_partner=False)
                else:
                    st.info("You haven't logged your mood today.")
                    if st.button("Log Mood", key="log_mood_home"):
                        st.session_state.active_page = "Mood"
                        st.experimental_rerun()
            
            with col2:
                st.markdown(f"#### {st.session_state.partner['name']}'s Mood")
                
                if mood_data.get('partner'):
                    partner_mood = mood_data['partner']
                    display_mood_card(partner_mood, is_partner=True)
                else:
                    st.info(f"{st.session_state.partner['name']} hasn't logged their mood today.")
    except Exception as e:
        st.error(f"Error loading mood data: {str(e)}")

def display_mood_card(mood, is_partner=False):
    """Display a mood card"""
    rating = mood.get('rating', 0)
    
    # Define color based on rating
    if rating >= 8:
        color = "green"
        emoji = "😃"
    elif rating >= 6:
        color = "lightgreen"
        emoji = "🙂"
    elif rating >= 4:
        color = "orange"
        emoji = "😐"
    else:
        color = "red"
        emoji = "😔"
    
    # Display mood card
    card_html = f"""
    <div style="
        padding: 10px 15px;
        border-radius: 10px;
        background-color: {color}20;
        border: 1px solid {color};
        margin-bottom: 10px;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="font-size: 32px; margin-right: 10px;">{emoji}</div>
            <div style="font-size: 24px; font-weight: bold;">{rating}/10</div>
        </div>
    """
    
    if mood.get('notes'):
        card_html += f'<div style="margin-top: 5px;">{mood["notes"]}</div>'
    
    if mood.get('tags') and len(mood['tags']) > 0:
        card_html += '<div style="margin-top: 8px; display: flex; flex-wrap: wrap;">'
        for tag in mood['tags']:
            card_html += f'<span style="background-color: {color}40; padding: 3px 8px; border-radius: 10px; margin-right: 5px; margin-bottom: 5px; font-size: 12px;">{tag}</span>'
        card_html += '</div>'
    
    card_html += "</div>"
    
    st.markdown(card_html, unsafe_allow_html=True)

def display_upcoming_events():
    """Display upcoming calendar events"""
    st.markdown("### Upcoming Events")
    
    try:
        # Get today's date and date one week from now
        today = datetime.now().strftime('%Y-%m-%d')
        one_week_later = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{API_URL}/api/calendar/events",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            params={"start_date": today, "end_date": one_week_later, "limit": 5}
        )
        
        if response.status_code == 200:
            events = response.json()
            
            if events and len(events) > 0:
                for event in events:
                    # Format date for display
                    event_date = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
                    date_display = event_date.strftime("%a, %b %d")
                    time_display = event_date.strftime("%I:%M %p") if not event.get('all_day') else "All day"
                    
                    # Display event card
                    st.markdown(
                        f"""
                        <div style="
                            padding: 10px 15px;
                            border-radius: 5px;
                            background-color: #f0f2f6;
                            margin-bottom: 10px;
                        ">
                            <div style="font-weight: bold;">{event['title']}</div>
                            <div style="display: flex; justify-content: space-between; font-size: 14px; color: #555;">
                                <div>{date_display}</div>
                                <div>{time_display}</div>
                            </div>
                            {f'<div style="font-size: 13px; margin-top: 5px;">{event["location"]}</div>' if event.get('location') else ''}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No upcoming events for the next week.")
                
            if st.button("View Calendar", key="view_calendar_home"):
                st.session_state.active_page = "Calendar"
                st.experimental_rerun()
    except Exception as e:
        st.error(f"Error loading calendar events: {str(e)}")

def display_daily_prompt():
    """Display daily conversation prompt"""
    st.markdown("### Daily Conversation Starter")
    
    try:
        response = requests.get(
            f"{API_URL}/api/prompts/daily",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        
        if response.status_code == 200:
            prompt = response.json()
            
            st.markdown(
                f"""
                <div style="
                    padding: 15px;
                    border-radius: 10px;
                    background-color: #f0f8ff;
                    border: 1px solid #add8e6;
                    margin-bottom: 10px;
                ">
                    <div style="font-style: italic; font-weight: bold;">{prompt['content']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            if prompt.get('answered'):
                st.success("You've both responded to this prompt!")
            else:
                if st.button("Respond", key="respond_prompt_home"):
                    # Store prompt ID in session state and navigate to prompts page
                    st.session_state.active_prompt = prompt['prompt_id']
                    st.session_state.active_page = "Prompts"
                    st.experimental_rerun()
    except Exception as e:
        st.error(f"Error loading daily prompt: {str(e)}")

def display_recent_messages():
    """Display recent messages"""
    st.markdown("### Recent Messages")
    
    try:
        if not st.session_state.partner:
            st.info("Connect with your partner to start messaging!")
            return
            
        response = requests.get(
            f"{API_URL}/api/messages/?limit=5",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        
        if response.status_code == 200:
            messages = response.json()
            
            if messages and len(messages) > 0:
                for message in messages:
                    # Determine if message is from partner
                    is_from_partner = message['sender_id'] != st.session_state.user['user_id']
                    sender_name = st.session_state.partner['name'] if is_from_partner else "You"
                    
                    # Format date for display
                    message_date = datetime.fromisoformat(message['created_at'].replace('Z', '+00:00'))
                    time_ago = get_time_ago(message_date)
                    
                    # Display message card
                    st.markdown(
                        f"""
                        <div style="
                            padding: 10px 15px;
                            border-radius: 10px;
                            background-color: {'#e6f7ff' if is_from_partner else '#f0f0f0'};
                            margin-bottom: 10px;
                            border-left: 3px solid {'#0066cc' if is_from_partner else '#888'};
                        ">
                            <div style="font-weight: bold; font-size: 14px;">{sender_name}</div>
                            <div style="margin: 5px 0;">{message['content'][:100] + ('...' if len(message['content']) > 100 else '')}</div>
                            <div style="font-size: 12px; color: #777; text-align: right;">{time_ago}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No messages yet. Start a conversation!")
                
            if st.button("View Messages", key="view_messages_home"):
                st.session_state.active_page = "Messages"
                st.experimental_rerun()
    except Exception as e:
        st.error(f"Error loading messages: {str(e)}")

def display_activity_suggestions():
    """Display activity suggestions"""
    st.markdown("### Activity Suggestions")
    
    try:
        response = requests.get(
            f"{API_URL}/api/activities/suggested?limit=3",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        
        if response.status_code == 200:
            activities = response.json()
            
            if activities and len(activities) > 0:
                for activity in activities:
                    st.markdown(
                        f"""
                        <div style="
                            padding: 10px 15px;
                            border-radius: 10px;
                            background-color: #f9f0ff;
                            border: 1px solid #e6ccff;
                            margin-bottom: 10px;
                        ">
                            <div style="font-weight: bold;">{activity['title']}</div>
                            <div style="margin: 5px 0; font-size: 14px;">{activity['description'][:100] + ('...' if len(activity['description']) > 100 else '')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    if st.button("Plan This Activity", key=f"plan_activity_{activity['activity_id']}"):
                        # Store activity and navigate to activities page
                        st.session_state.selected_activity = activity
                        st.session_state.active_page = "Activities"
                        st.experimental_rerun()
            else:
                st.info("No activity suggestions available.")
                
            if st.button("View More Activities", key="view_activities_home"):
                st.session_state.active_page = "Activities"
                st.experimental_rerun()
    except Exception as e:
        st.error(f"Error loading activity suggestions: {str(e)}")

def get_time_ago(timestamp):
    """Get relative time ago from timestamp"""
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        if diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        else:
            return timestamp.strftime("%b %d, %Y")
    else:
        hours = diff.seconds // 3600
        if hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        
        minutes = (diff.seconds % 3600) // 60
        if minutes > 0:
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        
        return "Just now"