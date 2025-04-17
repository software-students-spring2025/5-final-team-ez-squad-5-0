"""
Calendar component for the Together web application
"""
import os
import streamlit as st
import requests
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# API URL
API_URL = os.environ.get('API_URL', 'http://localhost:5000')

def display_calendar():
    """Display calendar interface"""
    st.title("Calendar")
    
    # Create tabs for different calendar views
    tab1, tab2, tab3 = st.tabs(["Calendar View", "Upcoming Events", "Add Event"])
    
    with tab1:
        display_calendar_view()
    
    with tab2:
        display_upcoming_events()
    
    with tab3:
        create_event_form()

def display_calendar_view():
    """Display calendar view"""
    st.subheader("Calendar View")
    
    # Month selection
    today = datetime.now()
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_month = st.selectbox("Month", options=months, index=today.month - 1)
    with col2:
        selected_year = st.selectbox("Year", options=range(today.year - 1, today.year + 5), index=1)
    
    # Calculate month dates
    month_idx = months.index(selected_month) + 1
    first_day = datetime(selected_year, month_idx, 1)
    
    # Get the number of days in the month
    if month_idx == 12:
        last_day = datetime(selected_year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(selected_year, month_idx + 1, 1) - timedelta(days=1)
    
    num_days = last_day.day
    
    # Get the day of the week of the first day (0 = Monday, 6 = Sunday)
    first_weekday = first_day.weekday()
    
    # Adjust for Sunday as first day of the week
    if first_weekday == 6:
        first_weekday = 0
    else:
        first_weekday += 1
    
    # Create calendar grid
    # Header
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        st.markdown("<div style='text-align: center;'><strong>Sun</strong></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div style='text-align: center;'><strong>Mon</strong></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div style='text-align: center;'><strong>Tue</strong></div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div style='text-align: center;'><strong>Wed</strong></div>", unsafe_allow_html=True)
    with col5:
        st.markdown("<div style='text-align: center;'><strong>Thu</strong></div>", unsafe_allow_html=True)
    with col6:
        st.markdown("<div style='text-align: center;'><strong>Fri</strong></div>", unsafe_allow_html=True)
    with col7:
        st.markdown("<div style='text-align: center;'><strong>Sat</strong></div>", unsafe_allow_html=True)
    
    # Get events for the selected month
    # In a real app, we would fetch events from the API
    # For simulation, create some sample events
    events = [
        {
            "event_id": "evt1",
            "title": "Date Night",
            "start_time": datetime(selected_year, month_idx, 15, 19, 0).isoformat(),
            "location": "Italian Restaurant"
        },
        {
            "event_id": "evt2",
            "title": "Anniversary",
            "start_time": datetime(selected_year, month_idx, 20).isoformat(),
            "all_day": True
        },
        {
            "event_id": "evt3",
            "title": "Virtual Game Night",
            "start_time": datetime(selected_year, month_idx, 25, 20, 0).isoformat()
        }
    ]
    
    # Create a dictionary to store events by day
    events_by_day = {}
    for event in events:
        event_date = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00') if 'Z' in event['start_time'] else event['start_time'])
        day = event_date.day
        if day not in events_by_day:
            events_by_day[day] = []
        events_by_day[day].append(event)
    
    # Generate calendar days
    days = [0] * first_weekday + list(range(1, num_days + 1))
    
    # Fill in trailing cells to make complete weeks
    while len(days) % 7 != 0:
        days.append(0)
    
    # Display calendar
    for week_start in range(0, len(days), 7):
        week = days[week_start:week_start + 7]
        cols = st.columns(7)
        
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    # Empty cell
                    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
                else:
                    # Check if today
                    is_today = (day == today.day and month_idx == today.month and selected_year == today.year)
                    
                    # Day cell style
                    day_style = "text-align: center; padding: 5px; background-color: "
                    if is_today:
                        day_style += "#e6f7ff; border-radius: 50%; font-weight: bold;"
                    else:
                        day_style += "transparent;"
                    
                    st.markdown(f"<div style='{day_style}'>{day}</div>", unsafe_allow_html=True)
                    
                    # Display events for this day
                    if day in events_by_day:
                        for event in events_by_day[day]:
                            event_date = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00') if 'Z' in event['start_time'] else event['start_time'])
                            time_str = event_date.strftime("%I:%M %p") if not event.get('all_day') else "All day"
                            
                            st.markdown(
                                f"""
                                <div style="
                                    padding: 3px 5px;
                                    background-color: #f0f2f6;
                                    border-left: 3px solid #5778a4;
                                    margin-bottom: 2px;
                                    border-radius: 3px;
                                    font-size: 0.8em;
                                    overflow: hidden;
                                    white-space: nowrap;
                                    text-overflow: ellipsis;
                                ">
                                    <div style="font-weight: bold;">{event['title']}</div>
                                    <div style="font-size: 0.8em;">{time_str}</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

def display_upcoming_events():
    """Display upcoming calendar events"""
    st.subheader("Upcoming Events")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        days_ahead = st.selectbox(
            "Time Range",
            options=["7 days", "30 days", "90 days", "All upcoming"],
            index=0
        )
    
    # Calculate date range
    today = datetime.now().date()
    if days_ahead == "7 days":
        end_date = today + timedelta(days=7)
    elif days_ahead == "30 days":
        end_date = today + timedelta(days=30)
    elif days_ahead == "90 days":
        end_date = today + timedelta(days=90)
    else:
        end_date = today + timedelta(days=365)  # Show events up to a year ahead
    
    try:
        # In a real app, we would fetch events from the API
        # For simulation, create some sample events
        events = [
            {
                "event_id": "evt1",
                "title": "Date Night",
                "start_time": (datetime.now() + timedelta(days=2)).replace(hour=19, minute=0).isoformat(),
                "location": "Italian Restaurant",
                "description": "Dinner at our favorite Italian place"
            },
            {
                "event_id": "evt2",
                "title": "Anniversary",
                "start_time": (datetime.now() + timedelta(days=15)).replace(hour=0, minute=0).isoformat(),
                "all_day": True,
                "description": "Our anniversary celebration"
            },
            {
                "event_id": "evt3",
                "title": "Virtual Game Night",
                "start_time": (datetime.now() + timedelta(days=7)).replace(hour=20, minute=0).isoformat(),
                "description": "Playing online games with friends"
            }
        ]
        
        # Sort events by date
        events.sort(key=lambda x: x['start_time'])
        
        if not events:
            st.info("No upcoming events found.")
        else:
            # Display events
            for event in events:
                # Format date for display
                event_date = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00') if 'Z' in event['start_time'] else event['start_time'])
                date_display = event_date.strftime("%A, %B %d, %Y")
                time_display = event_date.strftime("%I:%M %p") if not event.get('all_day') else "All day"
                
                # Display event card
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"### {event['title']}")
                        st.markdown(f"**When:** {date_display} at {time_display}")
                        
                        if event.get('location'):
                            st.markdown(f"**Where:** {event['location']}")
                        
                        if event.get('description'):
                            st.markdown(f"**Description:** {event['description']}")
                    
                    with col2:
                        # Edit button
                        if st.button("Edit", key=f"edit_{event['event_id']}"):
                            # Store event data in session state for editing
                            st.session_state.edit_event = event
                            st.experimental_rerun()
                        
                        # Delete button
                        if st.button("Delete", key=f"delete_{event['event_id']}"):
                            # In a real app, we would delete the event via API
                            st.success("Event deleted!")
                            st.experimental_rerun()
                    
                    st.markdown("---")
    except Exception as e:
        st.error(f"Error loading events: {str(e)}")
        st.info("This is a simulation. In a real environment, this would connect to the API.")

def create_event_form():
    """Display form to create a new calendar event"""
    st.subheader("Add New Event")
    
    # Check if editing an event
    editing = 'edit_event' in st.session_state
    
    if editing:
        form_title = "Edit Event"
        event = st.session_state.edit_event
        button_text = "Update Event"
    else:
        form_title = "Create New Event"
        event = {
            "title": "",
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(hours=1)).isoformat(),
            "location": "",
            "description": "",
            "all_day": False
        }
        button_text = "Create Event"
    
    with st.form(f"{form_title.lower().replace(' ', '_')}_form", clear_on_submit=not editing):
        title = st.text_input("Event Title", value=event.get('title', ''))
        
        all_day = st.checkbox("All Day Event", value=event.get('all_day', False))
        
        if all_day:
            col1, col2 = st.columns(2)
            
            with col1:
                # Parse date from ISO format
                start_date_value = datetime.fromisoformat(event.get('start_time', '').replace('Z', '+00:00') if 'Z' in event.get('start_time', '') else event.get('start_time', '')) if event.get('start_time') else datetime.now()
                start_date = st.date_input("Date", value=start_date_value.date())
            
            # No time input for all-day events
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                # Parse date from ISO format
                start_date_value = datetime.fromisoformat(event.get('start_time', '').replace('Z', '+00:00') if 'Z' in event.get('start_time', '') else event.get('start_time', '')) if event.get('start_time') else datetime.now()
                start_date = st.date_input("Start Date", value=start_date_value.date())
            
            with col2:
                start_time = st.time_input("Start Time", value=start_date_value.time())
            
            col3, col4 = st.columns(2)
            
            with col3:
                # Parse end date from ISO format
                end_date_value = datetime.fromisoformat(event.get('end_time', '').replace('Z', '+00:00') if 'Z' in event.get('end_time', '') else event.get('end_time', '')) if event.get('end_time') else datetime.now() + timedelta(hours=1)
                end_date = st.date_input("End Date", value=end_date_value.date())
            
            with col4:
                end_time = st.time_input("End Time", value=end_date_value.time())
        
        location = st.text_input("Location (Optional)", value=event.get('location', ''))
        description = st.text_area("Description (Optional)", value=event.get('description', ''), height=100)
        
        shared_with_partner = st.checkbox("Share with Partner", value=True)
        
        submit = st.form_submit_button(button_text)
        
        if submit:
            if not title:
                st.error("Please enter an event title")
                return
            
            # Prepare event data
            if all_day:
                # All-day event
                event_data = {
                    "title": title,
                    "start_time": datetime.combine(start_date, datetime.min.time()).isoformat(),
                    "all_day": True,
                    "shared": shared_with_partner
                }
            else:
                # Timed event
                start_datetime = datetime.combine(start_date, start_time)
                end_datetime = datetime.combine(end_date, end_time)
                
                # Validate date/time
                if end_datetime <= start_datetime:
                    st.error("End time must be after start time")
                    return
                
                event_data = {
                    "title": title,
                    "start_time": start_datetime.isoformat(),
                    "end_time": end_datetime.isoformat(),
                    "all_day": False,
                    "shared": shared_with_partner
                }
            
            # Add optional fields
            if location:
                event_data["location"] = location
            
            if description:
                event_data["description"] = description
            
            try:
                if editing:
                    # In a real app, we would update the event via API
                    # For simulation, show success message
                    st.success("Event updated!")
                    
                    # Clear edit session state
                    del st.session_state.edit_event
                else:
                    # In a real app, we would create the event via API
                    # For simulation, show success message
                    st.success("Event created!")
                
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")