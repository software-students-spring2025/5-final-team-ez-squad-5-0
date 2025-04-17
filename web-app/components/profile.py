"""
Profile component for the Together web application
"""
import os
import streamlit as st
import requests
from datetime import datetime

# API URL
API_URL = os.environ.get('API_URL', 'http://localhost:5000')

def display_profile():
    """Display profile interface"""
    st.title("Profile")
    
    # Create tabs for different profile views
    tab1, tab2, tab3 = st.tabs(["My Profile", "Relationship", "Settings"])
    
    with tab1:
        display_user_profile()
    
    with tab2:
        display_relationship_profile()
    
    with tab3:
        display_settings()

def display_user_profile():
    """Display user profile information"""
    st.header("My Profile")
    
    # Initialize user profile data
    if 'profile' not in st.session_state or not st.session_state.profile:
        # In a real app, we would fetch profile from the API
        # For simulation, create a sample profile
        st.session_state.profile = {
            "bio": "",
            "interests": [],
            "preferences": {
                "date_ideas": [],
                "communication_style": "",
                "love_language": ""
            },
            "photos": []
        }
    
    # Get current profile data
    profile = st.session_state.profile
    
    # Create form for profile editing
    with st.form("edit_profile_form"):
        st.subheader("Basic Information")
        name = st.text_input("Name", value=st.session_state.user['name'])
        email = st.text_input("Email", value=st.session_state.user['email'], disabled=True)
        
        st.subheader("About Me")
        bio = st.text_area("Bio", value=profile.get('bio', ''), 
                         help="Tell your partner a bit about yourself")
        
        st.subheader("Interests")
        st.markdown("Select interests or add your own")
        
        # Create columns for interests checkboxes
        col1, col2, col3 = st.columns(3)
        
        # Define common interests
        common_interests = [
            "Travel", "Movies", "Reading", "Music", "Cooking", 
            "Hiking", "Gaming", "Art", "Sports", "Fitness", 
            "Photography", "Yoga", "Dancing", "Writing", "Technology"
        ]
        
        # Split interests into columns
        interests_per_col = len(common_interests) // 3
        
        # Get current interests
        current_interests = profile.get('interests', [])
        
        # Create interest checkboxes
        selected_interests = []
        
        with col1:
            for interest in common_interests[:interests_per_col]:
                if st.checkbox(interest, value=(interest in current_interests), key=f"interest_{interest}"):
                    selected_interests.append(interest)
        
        with col2:
            for interest in common_interests[interests_per_col:interests_per_col*2]:
                if st.checkbox(interest, value=(interest in current_interests), key=f"interest_{interest}"):
                    selected_interests.append(interest)
        
        with col3:
            for interest in common_interests[interests_per_col*2:]:
                if st.checkbox(interest, value=(interest in current_interests), key=f"interest_{interest}"):
                    selected_interests.append(interest)
        
        # Custom interests
        custom_interests = st.text_input("Add custom interests (comma separated)")
        
        st.subheader("Relationship Preferences")
        
        # Love language
        love_language = st.selectbox(
            "Love Language",
            options=[
                "Words of Affirmation",
                "Acts of Service",
                "Receiving Gifts",
                "Quality Time",
                "Physical Touch",
                "Not sure yet"
            ],
            index=5 if not profile.get('preferences', {}).get('love_language') else 
                  ["Words of Affirmation", "Acts of Service", "Receiving Gifts", "Quality Time", "Physical Touch", "Not sure yet"].index(profile.get('preferences', {}).get('love_language'))
        )
        
        # Communication style
        communication_style = st.selectbox(
            "Communication Style",
            options=[
                "Direct and straightforward",
                "Emotional and expressive",
                "Thoughtful and reserved",
                "Analytical and logical",
                "Casual and easygoing",
                "Not sure yet"
            ],
            index=5 if not profile.get('preferences', {}).get('communication_style') else
                  ["Direct and straightforward", "Emotional and expressive", "Thoughtful and reserved", "Analytical and logical", "Casual and easygoing", "Not sure yet"].index(profile.get('preferences', {}).get('communication_style'))
        )
        
        # Date ideas
        st.markdown("Favorite Date Ideas")
        date_ideas = st.text_area(
            "Share some of your favorite date ideas (one per line)",
            value="\n".join(profile.get('preferences', {}).get('date_ideas', [])) if profile.get('preferences', {}).get('date_ideas') else ""
        )
        
        # Submit button
        submit = st.form_submit_button("Save Profile")
        
        if submit:
            # Parse custom interests
            if custom_interests:
                custom_interests_list = [interest.strip() for interest in custom_interests.split(",") if interest.strip()]
                selected_interests.extend(custom_interests_list)
            
            # Parse date ideas
            date_ideas_list = [idea.strip() for idea in date_ideas.split("\n") if idea.strip()]
            
            # Update profile data
            updated_profile = {
                "bio": bio,
                "interests": selected_interests,
                "preferences": {
                    "date_ideas": date_ideas_list,
                    "communication_style": communication_style if communication_style != "Not sure yet" else "",
                    "love_language": love_language if love_language != "Not sure yet" else ""
                },
                "photos": profile.get('photos', [])
            }
            
            try:
                # In a real app, we would update profile via API
                # For simulation, update session state
                st.session_state.profile = updated_profile
                st.session_state.user['name'] = name
                
                st.success("Profile updated successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error updating profile: {str(e)}")

def display_relationship_profile():
    """Display relationship information"""
    st.header("Relationship")
    
    # Check if user has a partner
    if not st.session_state.partner:
        st.info("You are not connected with a partner yet.")
        
        # Display partner invitation form
        with st.form("invite_partner_form"):
            st.subheader("Invite Your Partner")
            st.markdown("Send an invitation to your partner to connect on Together.")
            
            partner_email = st.text_input("Partner's Email")
            submit = st.form_submit_button("Send Invitation")
            
            if submit:
                if not partner_email:
                    st.error("Please enter your partner's email")
                    return
                
                try:
                    # In a real app, we would send invitation via API
                    # For simulation, show success message
                    st.success(f"Invitation sent to {partner_email}!")
                    
                    # Update user's partner status
                    st.session_state.user['partner_status'] = 'invited'
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error sending invitation: {str(e)}")
        
        return
    
    # User has a partner, display relationship information
    partner = st.session_state.partner
    
    st.markdown(f"### Connected with {partner['name']}")
    st.markdown(f"**Email:** {partner['email']}")
    
    # Get relationship data
    relationship = st.session_state.relationship if 'relationship' in st.session_state else {
        "anniversary": (datetime.now() - timedelta(days=365)).isoformat(),
        "nickname1": "",
        "nickname2": "",
        "settings": {
            "privacy_level": "private",
            "shared_calendar": True
        }
    }
    
    # Format anniversary date
    anniversary = datetime.fromisoformat(relationship['anniversary'].replace('Z', '+00:00') if 'Z' in relationship['anniversary'] else relationship['anniversary'])
    anniversary_str = anniversary.strftime("%B %d, %Y")
    
    st.markdown(f"**Anniversary:** {anniversary_str}")
    
    # Relationship settings
    with st.form("relationship_settings_form"):
        st.subheader("Relationship Settings")
        
        # Nicknames
        col1, col2 = st.columns(2)
        
        with col1:
            nickname1 = st.text_input("Your Nickname (Optional)", value=relationship.get('nickname1', ''))
        
        with col2:
            nickname2 = st.text_input(f"{partner['name']}'s Nickname (Optional)", value=relationship.get('nickname2', ''))
        
        # Anniversary date
        anniversary_date = st.date_input("Anniversary Date", value=anniversary.date())
        
        # Privacy settings
        privacy_level = st.selectbox(
            "Privacy Level",
            options=["Private", "Friends Only", "Public"],
            index=0 if relationship.get('settings', {}).get('privacy_level') == 'private' else 
                  1 if relationship.get('settings', {}).get('privacy_level') == 'friends' else 2
        )
        
        # Shared calendar
        shared_calendar = st.checkbox("Shared Calendar", value=relationship.get('settings', {}).get('shared_calendar', True))
        
        # Submit button
        submit = st.form_submit_button("Save Settings")
        
        if submit:
            # Update relationship settings
            updated_relationship = {
                "anniversary": datetime.combine(anniversary_date, datetime.min.time()).isoformat(),
                "nickname1": nickname1,
                "nickname2": nickname2,
                "settings": {
                    "privacy_level": privacy_level.lower().replace(' only', ''),
                    "shared_calendar": shared_calendar
                }
            }
            
            try:
                # In a real app, we would update relationship via API
                # For simulation, update session state
                st.session_state.relationship = updated_relationship
                
                st.success("Relationship settings updated!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error updating relationship: {str(e)}")

def display_settings():
    """Display app settings"""
    st.header("App Settings")
    
    with st.form("app_settings_form"):
        st.subheader("Notifications")
        
        # Notification settings
        enable_notifications = st.checkbox("Enable Notifications", value=True)
        
        # Notification types
        st.markdown("Notification Types")
        notify_messages = st.checkbox("New Messages", value=True)
        notify_events = st.checkbox("Calendar Events", value=True)
        notify_mood = st.checkbox("Partner's Mood Updates", value=True)
        notify_prompts = st.checkbox("Daily Conversation Prompts", value=True)
        
        st.subheader("Privacy")
        
        # Data sharing
        data_analytics = st.checkbox("Share Anonymous Usage Data for App Improvements", value=True)
        
        # Account settings
        st.subheader("Account")
        
        # Change password
        if st.checkbox("Change Password"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if current_password and new_password and confirm_password:
                # Validate passwords
                if new_password != confirm_password:
                    st.error("New passwords do not match")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters long")
        
        # Submit button
        submit = st.form_submit_button("Save Settings")
        
        if submit:
            # In a real app, we would save settings via API
            # For simulation, show success message
            st.success("Settings updated successfully!")
    
    # Danger zone
    st.markdown("---")
    st.subheader("Danger Zone")
    
    # Delete account button
    if st.button("Delete Account", type="primary", help="This action cannot be undone"):
        # Show confirmation dialog
        st.warning("Are you sure you want to delete your account? All your data will be permanently deleted.")
        
        # Confirm and cancel buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Yes, Delete Account", key="confirm_delete"):
                # In a real app, we would delete account via API
                # For simulation, logout user
                st.session_state.user = None
                st.session_state.access_token = None
                st.session_state.refresh_token = None
                st.experimental_rerun()
        
        with col2:
            if st.button("Cancel", key="cancel_delete"):
                st.experimental_rerun()
        