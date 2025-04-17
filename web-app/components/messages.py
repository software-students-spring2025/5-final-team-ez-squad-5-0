"""
Messaging component for the Together web application
"""
import os
import streamlit as st
import requests
from datetime import datetime, timedelta
import pytz

# API URL
API_URL = os.environ.get('API_URL', 'http://localhost:5000')

def display_messages():
    """Display messaging interface"""
    st.title("Messages")
    
    # Check if user has a partner
    if not st.session_state.partner:
        st.info("Connect with your partner to start messaging!")
        return
    
    # Display message history and input form
    col1, col2 = st.columns([3, 1])
    
    with col1:
        display_message_history()
        display_message_input()
    
    with col2:
        display_scheduled_messages()

def display_message_history():
    """Display message history"""
    st.markdown("### Conversation with " + st.session_state.partner['name'])
    
    # Create container for messages
    message_container = st.container()
    
    # Load messages
    try:
        response = requests.get(
            f"{API_URL}/api/messages/?limit=50",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        
        if response.status_code == 200:
            messages = response.json()
            
            # Reverse messages to show newest at bottom
            messages.reverse()
            
            # Group messages by date
            current_date = None
            
            with message_container:
                if not messages:
                    st.info("No messages yet. Start a conversation!")
                else:
                    for message in messages:
                        # Get message date for grouping
                        message_date = datetime.fromisoformat(message['created_at'].replace('Z', '+00:00'))
                        message_date_str = message_date.strftime("%A, %B %d, %Y")
                        
                        # Add date separator if date changes
                        if current_date != message_date_str:
                            current_date = message_date_str
                            st.markdown(f"<div style='text-align: center; margin: 20px 0; color: #888;'>{current_date}</div>", unsafe_allow_html=True)
                        
                        # Determine message sender
                        is_from_partner = message['sender_id'] != st.session_state.user['user_id']
                        sender_name = st.session_state.partner['name'] if is_from_partner else "You"
                        
                        # Format time
                        message_time = message_date.strftime("%I:%M %p")
                        
                        # Display message bubble
                        message_type = message.get('type', 'text')
                        message_content = message['content']
                        
                        if is_from_partner:
                            # Partner's message (left-aligned)
                            st.markdown(
                                f"""
                                <div style="display: flex; margin-bottom: 10px;">
                                    <div style="
                                        max-width: 80%;
                                        padding: 10px 15px;
                                        border-radius: 18px;
                                        background-color: #e6f7ff;
                                        position: relative;
                                    ">
                                        <div style="font-weight: bold; font-size: 12px; margin-bottom: 3px;">{sender_name}</div>
                                        <div>{message_content}</div>
                                        <div style="font-size: 10px; color: #888; text-align: right; margin-top: 2px;">{message_time}</div>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            # Your message (right-aligned)
                            st.markdown(
                                f"""
                                <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                                    <div style="
                                        max-width: 80%;
                                        padding: 10px 15px;
                                        border-radius: 18px;
                                        background-color: #dcf8c6;
                                        position: relative;
                                    ">
                                        <div>{message_content}</div>
                                        <div style="font-size: 10px; color: #888; text-align: right; margin-top: 2px;">{message_time}</div>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
        else:
            st.error("Failed to load messages. Please try again.")
    except Exception as e:
        st.error(f"Error loading messages: {str(e)}")

def display_message_input():
    """Display message input form"""
    st.markdown("---")
    
    # Create tabs for different message types
    tab1, tab2, tab3 = st.tabs(["Send Message", "Schedule Message", "Send Photo"])
    
    # Regular message
    with tab1:
        with st.form("send_message_form", clear_on_submit=True):
            message = st.text_area("Type a message", height=100)
            submit = st.form_submit_button("Send")
            
            if submit:
                if not message:
                    st.error("Please enter a message")
                    return
                
                try:
                    response = requests.post(
                        f"{API_URL}/api/messages/",
                        headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                        json={"content": message, "type": "text"}
                    )
                    
                    if response.status_code == 201:
                        st.success("Message sent!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to send message. Please try again.")
                except Exception as e:
                    st.error(f"Error sending message: {str(e)}")
    
    # Scheduled message
    with tab2:
        with st.form("schedule_message_form", clear_on_submit=True):
            scheduled_message = st.text_area("Type a message", height=100)
            
            # Date and time selection
            col1, col2 = st.columns(2)
            with col1:
                scheduled_date = st.date_input("Select date", min_value=datetime.now().date())
            with col2:
                scheduled_time = st.time_input("Select time")
            
            submit_scheduled = st.form_submit_button("Schedule Message")
            
            if submit_scheduled:
                if not scheduled_message:
                    st.error("Please enter a message")
                    return
                
                # Combine date and time
                scheduled_datetime = datetime.combine(scheduled_date, scheduled_time)
                
                # Check if scheduled time is in the future
                if scheduled_datetime <= datetime.now():
                    st.error("Please select a future date and time")
                    return
                
                try:
                    response = requests.post(
                        f"{API_URL}/api/messages/",
                        headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                        json={
                            "content": scheduled_message,
                            "type": "text",
                            "scheduled_for": scheduled_datetime.isoformat()
                        }
                    )
                    
                    if response.status_code == 201:
                        st.success("Message scheduled!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to schedule message. Please try again.")
                except Exception as e:
                    st.error(f"Error scheduling message: {str(e)}")
    
    # Photo message
    with tab3:
        with st.form("photo_message_form", clear_on_submit=True):
            uploaded_file = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])
            photo_caption = st.text_input("Caption (optional)")
            
            submit_photo = st.form_submit_button("Send Photo")
            
            if submit_photo:
                if uploaded_file is None:
                    st.error("Please upload a photo")
                    return
                
                st.warning("Photo sharing is coming soon!")
                # Here we would implement file upload to a storage service
                # and send a message with the photo URL

def display_scheduled_messages():
    """Display scheduled messages"""
    st.markdown("### Scheduled Messages")
    
    try:
        response = requests.get(
            f"{API_URL}/api/messages/scheduled",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        
        if response.status_code == 200:
            scheduled_messages = response.json()
            
            if scheduled_messages and len(scheduled_messages) > 0:
                for message in scheduled_messages:
                    # Format scheduled date for display
                    scheduled_date = datetime.fromisoformat(message['scheduled_for'].replace('Z', '+00:00'))
                    date_display = scheduled_date.strftime("%b %d, %Y")
                    time_display = scheduled_date.strftime("%I:%M %p")
                    
                    # Display scheduled message card
                    with st.container():
                        st.markdown(
                            f"""
                            <div style="
                                padding: 10px 15px;
                                border-radius: 10px;
                                background-color: #f0f0f0;
                                margin-bottom: 15px;
                                border: 1px solid #ddd;
                            ">
                                <div style="font-size: 12px; color: #777;">Scheduled for:</div>
                                <div style="font-weight: bold; font-size: 14px; margin-bottom: 5px;">{date_display} at {time_display}</div>
                                <div style="margin-bottom: 10px;">{message['content'][:50] + ('...' if len(message['content']) > 50 else '')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Cancel button
                        if st.button("Cancel", key=f"cancel_message_{message['message_id']}"):
                            try:
                                cancel_response = requests.delete(
                                    f"{API_URL}/api/messages/scheduled/{message['message_id']}",
                                    headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                                )
                                
                                if cancel_response.status_code == 200:
                                    st.success("Message canceled!")
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to cancel message. Please try again.")
                            except Exception as e:
                                st.error(f"Error canceling message: {str(e)}")
            else:
                st.info("No scheduled messages.")
    except Exception as e:
        st.error(f"Error loading scheduled messages: {str(e)}")