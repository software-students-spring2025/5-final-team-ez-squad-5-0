"""
Navigation components for the Together web application
"""
import streamlit as st
from components.auth import logout

def sidebar_navigation():
    """Display sidebar navigation and return the active page"""
    with st.sidebar:
        st.image("static/together-logo.png", width=200)
        st.markdown(f"### Welcome, {st.session_state.user['name']}")
        
        # Partner status
        if st.session_state.partner:
            st.markdown(f"Connected with: **{st.session_state.partner['name']}**")
        elif st.session_state.user.get('partner_status') == 'invited':
            st.markdown("**Partner invitation sent**")
        else:
            st.markdown("**Not connected with a partner**")
        
        st.markdown("---")
        
        # Navigation menu
        st.markdown("### Navigation")
        
        menu_items = [
            {"name": "Home", "icon": "🏠"},
            {"name": "Messages", "icon": "💌"},
            {"name": "Activities", "icon": "🎮"},
            {"name": "Prompts", "icon": "💬"},
            {"name": "Calendar", "icon": "📅"},
            {"name": "Mood", "icon": "🌈"},
            {"name": "Goals", "icon": "🎯"},
            {"name": "Profile", "icon": "👤"}
        ]
        
        for item in menu_items:
            if st.button(f"{item['icon']} {item['name']}", key=f"nav_{item['name']}"):
                st.session_state.active_page = item['name']
                return item['name']
        
        st.markdown("---")
        
        # Logout button
        if st.button("Logout"):
            logout()
    
    return st.session_state.active_page