"""
Together - A Relationship Enhancement Platform

Main Streamlit application.
"""
import os
import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# Import components
from components.auth import login_form, signup_form, load_user_data
from components.navigation import sidebar_navigation
from components.home import display_home
from components.messages import display_messages
from components.activities import display_activities
from components.prompts import display_prompts
from components.calendar import display_calendar
from components.mood import display_mood
from components.profile import display_profile
from components.goals import display_goals

# Set page configuration
st.set_page_config(
    page_title="Together - Relationship Enhancement App",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create session states for storing data
if 'user' not in st.session_state:
    st.session_state.user = None
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'refresh_token' not in st.session_state:
    st.session_state.refresh_token = None
if 'active_page' not in st.session_state:
    st.session_state.active_page = 'Home'
if 'partner' not in st.session_state:
    st.session_state.partner = None
if 'relationship' not in st.session_state:
    st.session_state.relationship = None
if 'profile' not in st.session_state:
    st.session_state.profile = None

# API URL
API_URL = os.environ.get('API_URL', 'http://localhost:5000')

def main():
    """Main application function"""
    # Custom CSS
    with open('static/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Check if user is logged in
    if st.session_state.access_token is None:
        # Display login/signup form
        st.markdown("# Together ❤️")
        st.markdown("#### Strengthen your relationship with shared experiences, better communication, and deeper connection.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Login")
            login_form()
        
        with col2:
            st.markdown("### Sign Up")
            signup_form()
        
        st.markdown("---")
        
        # Display app features
        st.markdown("## Features")
        
        feature_col1, feature_col2, feature_col3 = st.columns(3)
        
        with feature_col1:
            st.markdown("### 💌 Meaningful Communication")
            st.markdown("Share messages, schedule surprises, and stay connected throughout the day.")
        
        with feature_col2:
            st.markdown("### 🎯 Relationship Growth")
            st.markdown("Set goals together, track your progress, and celebrate your achievements.")
        
        with feature_col3:
            st.markdown("### 🏷️ Mood Tracking")
            st.markdown("Share how you're feeling and gain insights into your emotional patterns.")
        
        feature_col4, feature_col5, feature_col6 = st.columns(3)
        
        with feature_col4:
            st.markdown("### 📅 Shared Calendar")
            st.markdown("Plan activities and never miss important dates and anniversaries.")
        
        with feature_col5:
            st.markdown("### 💬 Conversation Starters")
            st.markdown("Discover thoughtful questions to deepen your connection.")
        
        with feature_col6:
            st.markdown("### 🎮 Activities")
            st.markdown("Find fun and meaningful activities to enjoy together, even at a distance.")
    else:
        # Load user data if needed
        if st.session_state.user and (st.session_state.partner is None or st.session_state.profile is None):
            load_user_data()
        
        # Display sidebar navigation
        active_page = sidebar_navigation()
        
        # Display the active page
        if active_page == 'Home':
            display_home()
        elif active_page == 'Messages':
            display_messages()
        elif active_page == 'Activities':
            display_activities()
        elif active_page == 'Prompts':
            display_prompts()
        elif active_page == 'Calendar':
            display_calendar()
        elif active_page == 'Mood':
            display_mood()
        elif active_page == 'Goals':
            display_goals()
        elif active_page == 'Profile':
            display_profile()

if __name__ == "__main__":
    main()