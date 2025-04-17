"""
Activities component for the Together web application
"""
import os
import streamlit as st
import requests
from datetime import datetime, timedelta

# API URL
API_URL = os.environ.get('API_URL', 'http://localhost:5000')

def display_activities():
    """Display activities interface"""
    st.title("Activities")
    
    # Create tabs for different activity views
    tab1, tab2, tab3 = st.tabs(["Planned Activities", "Activity Suggestions", "Create Activity"])
    
    with tab1:
        display_planned_activities()
    
    with tab2:
        display_activity_suggestions()
    
    with tab3:
        create_activity_form()

def display_planned_activities():
    """Display planned activities"""
    st.subheader("Planned Activities")
    
    # Activity filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        activity_type = st.selectbox(
            "Activity Type",
            options=["All", "Date", "Task", "Surprise", "Game", "Other"],
            index=0
        )
    
    with col2:
        completed = st.selectbox(
            "Status",
            options=["All", "Planned", "Completed"],
            index=0
        )
    
    # Convert filters to API parameters
    params = {}
    if activity_type != "All":
        params["type"] = activity_type.lower()
    
    if completed != "All":
        params["completed"] = completed == "Completed"
    
    try:
        # Make API request to get activities
        response = requests.get(
            f"{API_URL}/api/activities/",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            params=params
        )
        
        if response.status_code == 200:
            activities = response.json()
            
            if not activities:
                st.info("No activities found. Create a new activity to get started!")
            else:
                # Display activities
                for activity in activities:
                    # Create activity card
                    with st.container():
                        col_info, col_actions = st.columns([3, 1])
                        
                        with col_info:
                            # Activity title
                            st.markdown(f"### {activity['title']}")
                            
                            # Activity details
                            st.markdown(f"**Type:** {activity['type'].capitalize()}")
                            
                            if activity.get('scheduled_for'):
                                scheduled_date = datetime.fromisoformat(activity['scheduled_for'].replace('Z', '+00:00'))
                                st.markdown(f"**When:** {scheduled_date.strftime('%A, %B %d, %Y at %I:%M %p')}")
                            
                            if activity.get('location'):
                                st.markdown(f"**Where:** {activity['location']}")
                            
                            st.markdown(f"**Description:** {activity['description']}")
                            
                            # Status
                            if activity['completed']:
                                st.success("Completed")
                            else:
                                st.info("Planned")
                        
                        with col_actions:
                            # Complete button
                            if not activity['completed']:
                                if st.button("Mark as Done", key=f"complete_{activity['activity_id']}"):
                                    try:
                                        complete_response = requests.put(
                                            f"{API_URL}/api/activities/{activity['activity_id']}/complete",
                                            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                                        )
                                        
                                        if complete_response.status_code == 200:
                                            st.success("Activity marked as completed!")
                                            st.experimental_rerun()
                                        else:
                                            st.error("Failed to complete activity. Please try again.")
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                            
                            # Delete button
                            if st.button("Delete", key=f"delete_{activity['activity_id']}"):
                                try:
                                    delete_response = requests.delete(
                                        f"{API_URL}/api/activities/{activity['activity_id']}",
                                        headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                                    )
                                    
                                    if delete_response.status_code == 200:
                                        st.success("Activity deleted!")
                                        st.experimental_rerun()
                                    else:
                                        st.error("Failed to delete activity. Please try again.")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        
                        st.markdown("---")
        else:
            st.error(f"Failed to load activities: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error loading activities: {str(e)}")
        st.info("This is a simulation. In a real environment, this would connect to the API.")
        
        # Show sample activities
        sample_activities = [
            {
                "title": "Dinner at Italian Restaurant",
                "type": "date",
                "scheduled_for": (datetime.now() + timedelta(days=2)).isoformat(),
                "location": "Milano's Italian Bistro",
                "description": "Romantic dinner at our favorite restaurant",
                "completed": False
            },
            {
                "title": "Movie Night",
                "type": "date",
                "scheduled_for": (datetime.now() + timedelta(days=5)).isoformat(),
                "location": "Home",
                "description": "Watch the new sci-fi movie we've been wanting to see",
                "completed": False
            }
        ]
        
        for i, activity in enumerate(sample_activities):
            with st.container():
                col_info, col_actions = st.columns([3, 1])
                
                with col_info:
                    # Activity title
                    st.markdown(f"### {activity['title']}")
                    
                    # Activity details
                    st.markdown(f"**Type:** {activity['type'].capitalize()}")
                    
                    if activity.get('scheduled_for'):
                        scheduled_date = datetime.fromisoformat(activity['scheduled_for'].replace('Z', '+00:00') if 'Z' in activity['scheduled_for'] else activity['scheduled_for'])
                        st.markdown(f"**When:** {scheduled_date.strftime('%A, %B %d, %Y at %I:%M %p')}")
                    
                    if activity.get('location'):
                        st.markdown(f"**Where:** {activity['location']}")
                    
                    st.markdown(f"**Description:** {activity['description']}")
                    
                    # Status
                    if activity['completed']:
                        st.success("Completed")
                    else:
                        st.info("Planned")
                
                with col_actions:
                    # Complete button
                    if not activity['completed']:
                        st.button("Mark as Done", key=f"sample_complete_{i}")
                    
                    # Delete button
                    st.button("Delete", key=f"sample_delete_{i}")
                
                st.markdown("---")

def display_activity_suggestions():
    """Display activity suggestions"""
    st.subheader("Suggested Activities")
    
    activity_type = st.selectbox(
        "Activity Type",
        options=["Date", "Game", "Surprise", "Task", "Other"],
        index=0,
        key="suggestion_type"
    )
    
    try:
        # Make API request to get suggested activities
        response = requests.get(
            f"{API_URL}/api/activities/suggested",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            params={"type": activity_type.lower(), "limit": 10}
        )
        
        if response.status_code == 200:
            suggestions = response.json()
            
            if not suggestions:
                st.info("No activity suggestions found for this category.")
            else:
                # Display suggestions
                for suggestion in suggestions:
                    with st.container():
                        col_info, col_actions = st.columns([3, 1])
                        
                        with col_info:
                            # Suggestion title
                            st.markdown(f"### {suggestion['title']}")
                            
                            # Suggestion description
                            st.markdown(f"{suggestion['description']}")
                            
                            # Tags if available
                            if suggestion.get('tags'):
                                st.markdown(f"**Tags:** {', '.join(suggestion['tags'])}")
                        
                        with col_actions:
                            # Plan button
                            if st.button("Plan This", key=f"plan_{suggestion.get('suggestion_id', hash(suggestion['title']))}"):
                                # Pre-fill activity form with suggestion data
                                st.session_state.new_activity_title = suggestion['title']
                                st.session_state.new_activity_description = suggestion['description']
                                st.session_state.new_activity_type = suggestion['type']
                                
                                # Switch to the create activity tab
                                st.experimental_rerun()
                        
                        st.markdown("---")
        else:
            st.error(f"Failed to load suggestions: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error loading suggestions: {str(e)}")
        st.info("This is a simulation. In a real environment, this would connect to the API.")
        
        # Show sample suggestions
        sample_suggestions = [
            {
                "title": "Cook a New Recipe Together",
                "description": "Pick a cuisine you've never tried making before and cook a meal together. This is a fun way to learn new skills and bond over the experience.",
                "type": "date",
                "tags": ["cooking", "learning", "teamwork"]
            },
            {
                "title": "Stargazing Picnic",
                "description": "Pack a picnic and head somewhere with minimal light pollution for an evening of stargazing. Bring a blanket, some snacks, and download a star map app to identify constellations.",
                "type": "date",
                "tags": ["nature", "romantic", "relaxing"]
            },
            {
                "title": "Memory Lane Photo Challenge",
                "description": "Each of you selects 5 photos that represent important moments in your relationship and share the stories behind them. This helps strengthen your shared narrative and appreciate your journey together.",
                "type": "game",
                "tags": ["reflection", "communication", "memories"]
            }
        ]
        
        for i, suggestion in enumerate(sample_suggestions):
            with st.container():
                col_info, col_actions = st.columns([3, 1])
                
                with col_info:
                    # Suggestion title
                    st.markdown(f"### {suggestion['title']}")
                    
                    # Suggestion description
                    st.markdown(f"{suggestion['description']}")
                    
                    # Tags if available
                    if suggestion.get('tags'):
                        st.markdown(f"**Tags:** {', '.join(suggestion['tags'])}")
                
                with col_actions:
                    # Plan button
                    st.button("Plan This", key=f"sample_plan_{i}")
                
                st.markdown("---")

def create_activity_form():
    """Display form to create a new activity"""
    st.subheader("Create New Activity")
    
    # Initialize session state for form fields
    if 'new_activity_title' not in st.session_state:
        st.session_state.new_activity_title = ""
    
    if 'new_activity_description' not in st.session_state:
        st.session_state.new_activity_description = ""
    
    if 'new_activity_type' not in st.session_state:
        st.session_state.new_activity_type = "date"
    
    # Create form
    with st.form("create_activity_form", clear_on_submit=True):
        title = st.text_input("Activity Title", value=st.session_state.new_activity_title)
        
        activity_type = st.selectbox(
            "Activity Type",
            options=["Date", "Task", "Surprise", "Game", "Other"],
            index=["date", "task", "surprise", "game", "other"].index(st.session_state.new_activity_type) if st.session_state.new_activity_type in ["date", "task", "surprise", "game", "other"] else 0
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            scheduled_date = st.date_input("Date", value=datetime.now().date() + timedelta(days=1))
        
        with col2:
            scheduled_time = st.time_input("Time", value=datetime.now().time())
        
        location = st.text_input("Location (Optional)")
        
        description = st.text_area("Description", value=st.session_state.new_activity_description, height=100)
        
        shared = st.checkbox("Share with Partner", value=True)
        
        submit = st.form_submit_button("Create Activity")
        
        if submit:
            if not title or not description:
                st.error("Please fill in all required fields")
            else:
                # Combine date and time
                scheduled_datetime = datetime.combine(scheduled_date, scheduled_time)
                
                # Format for API
                activity_data = {
                    "title": title,
                    "type": activity_type.lower(),
                    "description": description,
                    "scheduled_for": scheduled_datetime.isoformat(),
                    "shared": shared
                }
                
                if location:
                    activity_data["location"] = location
                
                try:
                    # Make API request to create activity
                    response = requests.post(
                        f"{API_URL}/api/activities/",
                        headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                        json=activity_data
                    )
                    
                    if response.status_code == 201:
                        st.success("Activity created successfully!")
                        
                        # Clear session state
                        st.session_state.new_activity_title = ""
                        st.session_state.new_activity_description = ""
                        st.session_state.new_activity_type = "date"
                        
                        # Rerun to refresh the page
                        st.experimental_rerun()
                    else:
                        st.error(f"Failed to create activity: {response.json().get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error creating activity: {str(e)}")
                    st.success("This is a simulation. In a real environment, the activity would be created.")
