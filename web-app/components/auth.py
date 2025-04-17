"""
Authentication components for the Together web application
"""
import os
import streamlit as st
import requests
from datetime import datetime

# API URL
API_URL = os.environ.get('API_URL', 'http://localhost:5000')

def login_form():
    """Display login form"""
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
                return
            
            try:
                response = requests.post(
                    f"{API_URL}/api/auth/login",
                    json={"email": email, "password": password}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Store user data and tokens in session state
                    st.session_state.user = data["user"]
                    st.session_state.access_token = data["access_token"]
                    st.session_state.refresh_token = data["refresh_token"]
                    
                    # Reload the page
                    st.experimental_rerun()
                else:
                    st.error(response.json().get("error", "Login failed. Please check your credentials."))
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

def signup_form():
    """Display signup form"""
    with st.form("signup_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        password_confirm = st.text_input("Confirm Password", type="password")
        birthdate = st.date_input("Birth Date (Optional)", value=None)
        
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if not name or not email or not password:
                st.error("Please fill in all required fields")
                return
            
            if password != password_confirm:
                st.error("Passwords do not match")
                return
            
            if len(password) < 8:
                st.error("Password must be at least 8 characters long")
                return
            
            try:
                # Format birthdate if provided
                birthdate_str = None
                if birthdate:
                    birthdate_str = birthdate.strftime('%Y-%m-%d')
                
                # Create user data
                user_data = {
                    "name": name,
                    "email": email,
                    "password": password,
                }
                
                # Add birthdate if provided
                if birthdate_str:
                    user_data["birthdate"] = birthdate_str
                
                response = requests.post(
                    f"{API_URL}/api/auth/register",
                    json=user_data
                )
                
                if response.status_code == 201:
                    data = response.json()
                    
                    # Store user data and tokens in session state
                    st.session_state.user = data["user"]
                    st.session_state.access_token = data["access_token"]
                    st.session_state.refresh_token = data["refresh_token"]
                    
                    # Reload the page
                    st.experimental_rerun()
                else:
                    st.error(response.json().get("error", "Registration failed. Please try again."))
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

def logout():
    """Log out the user"""
    # Clear session state
    for key in ["user", "access_token", "refresh_token", "partner", "relationship", "profile"]:
        if key in st.session_state:
            st.session_state[key] = None
    
    # Reload the page
    st.experimental_rerun()

def load_user_data():
    """Load user profile, partner, and relationship data"""
    try:
        # Get user profile
        profile_response = requests.get(
            f"{API_URL}/api/profiles/",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        
        if profile_response.status_code == 200:
            st.session_state.profile = profile_response.json()
        
        # Get relationship data
        relationship_response = requests.get(
            f"{API_URL}/api/profiles/relationship",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        
        if relationship_response.status_code == 200:
            data = relationship_response.json()
            
            if data.get("relationship_status") == "connected":
                st.session_state.relationship = data.get("relationship")
                st.session_state.partner = data.get("partner")
    except Exception as e:
        st.error(f"Error loading user data: {str(e)}")

def refresh_token():
    """Refresh access token"""
    if not st.session_state.refresh_token:
        logout()
        return False
    
    try:
        response = requests.post(
            f"{API_URL}/api/auth/refresh",
            headers={"Authorization": f"Bearer {st.session_state.refresh_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            return True
        else:
            logout()
            return False
    except Exception:
        logout()
        return False