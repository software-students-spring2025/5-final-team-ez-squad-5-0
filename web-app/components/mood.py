"""
Mood tracking component for the Together web application
"""
import os
import streamlit as st
import requests
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# API URL
API_URL = os.environ.get('API_URL', 'http://localhost:5000')

def display_mood():
    """Display mood tracking interface"""
    st.title("Mood Tracking")
    
    # Create tabs for different mood views
    tab1, tab2, tab3 = st.tabs(["Log Mood", "Mood History", "Mood Insights"])
    
    with tab1:
        log_mood_form()
    
    with tab2:
        display_mood_history()
    
    with tab3:
        display_mood_insights()

def log_mood_form():
    """Display form to log current mood"""
    st.header("How are you feeling today?")
    
    # Check if mood already logged today
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # In a real app, we would check if mood is already logged via API
        # For simulation, create a flag
        mood_logged = False
        
        if mood_logged:
            st.success("You've already logged your mood today!")
            
            # Show today's mood
            st.markdown("### Today's Mood")
            display_mood_card({
                "rating": 8,
                "date": today,
                "notes": "Feeling productive and happy today!",
                "tags": ["productive", "happy", "energetic"]
            }, is_today=True)
            
            # Edit button
            if st.button("Edit Today's Mood"):
                # Reset the mood_logged flag
                mood_logged = False
                st.experimental_rerun()
        else:
            # Display mood logging form
            with st.form("log_mood_form"):
                # Mood rating slider
                mood_rating = st.slider(
                    "Rate your mood (1-10)",
                    min_value=1,
                    max_value=10,
                    value=7,
                    help="1 = Very bad, 10 = Excellent"
                )
                
                # Mood emoji display
                cols = st.columns(10)
                for i in range(1, 11):
                    with cols[i-1]:
                        if i == mood_rating:
                            st.markdown(get_mood_emoji(i), unsafe_allow_html=True)
                            st.markdown(f"<div style='text-align: center; font-weight: bold;'>{i}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(get_mood_emoji(i, selected=False), unsafe_allow_html=True)
                            st.markdown(f"<div style='text-align: center;'>{i}</div>", unsafe_allow_html=True)
                
                # Notes
                mood_notes = st.text_area("Notes (Optional)", placeholder="How are you feeling? What's on your mind?")
                
                # Tags
                st.markdown("**Tags** (Optional)")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    happy = st.checkbox("Happy")
                    calm = st.checkbox("Calm")
                    energetic = st.checkbox("Energetic")
                
                with col2:
                    tired = st.checkbox("Tired")
                    stressed = st.checkbox("Stressed")
                    anxious = st.checkbox("Anxious")
                
                with col3:
                    productive = st.checkbox("Productive")
                    loving = st.checkbox("Loving")
                    creative = st.checkbox("Creative")
                
                # Custom tag
                custom_tag = st.text_input("Add a custom tag")
                
                # Share with partner option
                share_with_partner = st.checkbox("Share with partner", value=True)
                
                # Submit button
                submit = st.form_submit_button("Log Mood")
                
                if submit:
                    # Collect selected tags
                    tags = []
                    if happy:
                        tags.append("happy")
                    if calm:
                        tags.append("calm")
                    if energetic:
                        tags.append("energetic")
                    if tired:
                        tags.append("tired")
                    if stressed:
                        tags.append("stressed")
                    if anxious:
                        tags.append("anxious")
                    if productive:
                        tags.append("productive")
                    if loving:
                        tags.append("loving")
                    if creative:
                        tags.append("creative")
                    
                    if custom_tag:
                        tags.append(custom_tag.lower())
                    
                    # Prepare mood data
                    mood_data = {
                        "rating": mood_rating,
                        "date": today,
                        "notes": mood_notes,
                        "tags": tags,
                        "share_with_partner": share_with_partner
                    }
                    
                    try:
                        # In a real app, we would submit the mood via API
                        # For simulation, show success message
                        st.success("Mood logged successfully!")
                        
                        # Display the logged mood
                        display_mood_card(mood_data, is_today=True)
                    except Exception as e:
                        st.error(f"Error logging mood: {str(e)}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def display_mood_history():
    """Display mood history"""
    st.header("Mood History")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        time_range = st.selectbox(
            "Time Range",
            options=["Last 7 days", "Last 30 days", "Last 3 months", "All time"],
            index=0
        )
    
    with col2:
        include_partner = st.checkbox("Include Partner's Mood", value=True)
    
    # Calculate date range
    today = datetime.now().date()
    if time_range == "Last 7 days":
        start_date = today - timedelta(days=7)
    elif time_range == "Last 30 days":
        start_date = today - timedelta(days=30)
    elif time_range == "Last 3 months":
        start_date = today - timedelta(days=90)
    else:
        start_date = today - timedelta(days=365)  # Show up to a year of history
    
    try:
        # In a real app, we would fetch mood history from the API
        # For simulation, create some sample mood data
        user_moods = [
            {
                "rating": 8,
                "date": (today - timedelta(days=0)).strftime('%Y-%m-%d'),
                "notes": "Feeling productive and happy today!",
                "tags": ["productive", "happy", "energetic"]
            },
            {
                "rating": 6,
                "date": (today - timedelta(days=1)).strftime('%Y-%m-%d'),
                "notes": "A bit tired but otherwise okay.",
                "tags": ["tired"]
            },
            {
                "rating": 7,
                "date": (today - timedelta(days=3)).strftime('%Y-%m-%d'),
                "notes": "Good day overall.",
                "tags": ["happy", "calm"]
            },
            {
                "rating": 9,
                "date": (today - timedelta(days=5)).strftime('%Y-%m-%d'),
                "notes": "Amazing day! Everything went well.",
                "tags": ["happy", "energetic", "productive"]
            }
        ]
        
        partner_moods = []
        if include_partner and st.session_state.partner:
            partner_moods = [
                {
                    "rating": 7,
                    "date": (today - timedelta(days=0)).strftime('%Y-%m-%d'),
                    "notes": "Good day at work!",
                    "tags": ["productive", "happy"],
                    "is_partner": True
                },
                {
                    "rating": 5,
                    "date": (today - timedelta(days=2)).strftime('%Y-%m-%d'),
                    "notes": "Feeling a bit stressed with deadlines.",
                    "tags": ["stressed", "tired"],
                    "is_partner": True
                },
                {
                    "rating": 8,
                    "date": (today - timedelta(days=4)).strftime('%Y-%m-%d'),
                    "notes": "Great day! Went for a run and felt energized.",
                    "tags": ["energetic", "happy"],
                    "is_partner": True
                }
            ]
        
        # Combine and sort moods
        all_moods = user_moods + partner_moods
        all_moods.sort(key=lambda x: x['date'], reverse=True)
        
        # Display mood chart
        if all_moods:
            display_mood_chart(user_moods, partner_moods, start_date)
            
            # Display mood entries
            st.subheader("Mood Entries")
            
            current_date = None
            for mood in all_moods:
                mood_date = datetime.strptime(mood['date'], '%Y-%m-%d').date()
                
                # Skip moods outside the selected date range
                if mood_date < start_date:
                    continue
                
                # Add date separator if date changes
                if current_date != mood_date:
                    current_date = mood_date
                    
                    # Format date
                    if mood_date == today:
                        date_display = "Today"
                    elif mood_date == today - timedelta(days=1):
                        date_display = "Yesterday"
                    else:
                        date_display = mood_date.strftime("%A, %B %d, %Y")
                    
                    st.markdown(f"#### {date_display}")
                
                # Display mood card
                is_partner_mood = mood.get('is_partner', False)
                display_mood_card(mood, is_partner=is_partner_mood)
        else:
            st.info("No mood data available for the selected time range.")
    except Exception as e:
        st.error(f"Error loading mood history: {str(e)}")
        st.info("This is a simulation. In a real environment, this would connect to the API.")

def display_mood_insights():
    """Display mood insights and analysis"""
    st.header("Mood Insights")
    
    # Time period selection
    period = st.selectbox(
        "Time Period",
        options=["Last 7 days", "Last 30 days", "Last 3 months"],
        index=1
    )
    
    try:
        # In a real app, we would fetch mood insights from the API
        # For simulation, create some sample insights
        if period == "Last 7 days":
            time_range = 7
        elif period == "Last 30 days":
            time_range = 30
        else:
            time_range = 90
        
        # Generate sample data
        today = datetime.now().date()
        
        user_insights = {
            "average_rating": 7.5,
            "highest_rating": 9,
            "lowest_rating": 6,
            "trend": "improving",
            "common_tags": ["happy", "productive", "tired"]
        }
        
        partner_insights = None
        if st.session_state.partner:
            partner_insights = {
                "average_rating": 6.8,
                "highest_rating": 8,
                "lowest_rating": 5,
                "trend": "stable",
                "common_tags": ["energetic", "stressed", "happy"]
            }
        
        # Display insights
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Your Mood Insights")
            st.metric("Average Mood", f"{user_insights['average_rating']}/10")
            
            # Mood range
            st.markdown(f"**Range:** {user_insights['lowest_rating']} - {user_insights['highest_rating']}")
            
            # Mood trend
            trend_emoji = "📈" if user_insights['trend'] == "improving" else "📉" if user_insights['trend'] == "declining" else "➡️"
            st.markdown(f"**Trend:** {user_insights['trend'].capitalize()} {trend_emoji}")
            
            # Common tags
            st.markdown("**Common Moods:**")
            tags_html = ""
            for tag in user_insights['common_tags']:
                tags_html += f'<span style="background-color: #e6f7ff; padding: 3px 8px; border-radius: 10px; margin-right: 5px; margin-bottom: 5px; font-size: 14px;">{tag}</span>'
            
            st.markdown(f"<div style='margin-top: 8px; display: flex; flex-wrap: wrap;'>{tags_html}</div>", unsafe_allow_html=True)
        
        if partner_insights:
            with col2:
                st.subheader(f"{st.session_state.partner['name']}'s Insights")
                st.metric("Average Mood", f"{partner_insights['average_rating']}/10")
                
                # Mood range
                st.markdown(f"**Range:** {partner_insights['lowest_rating']} - {partner_insights['highest_rating']}")
                
                # Mood trend
                trend_emoji = "📈" if partner_insights['trend'] == "improving" else "📉" if partner_insights['trend'] == "declining" else "➡️"
                st.markdown(f"**Trend:** {partner_insights['trend'].capitalize()} {trend_emoji}")
                
                # Common tags
                st.markdown("**Common Moods:**")
                tags_html = ""
                for tag in partner_insights['common_tags']:
                    tags_html += f'<span style="background-color: #f9e6ff; padding: 3px 8px; border-radius: 10px; margin-right: 5px; margin-bottom: 5px; font-size: 14px;">{tag}</span>'
                
                st.markdown(f"<div style='margin-top: 8px; display: flex; flex-wrap: wrap;'>{tags_html}</div>", unsafe_allow_html=True)
        
        # Display correlation insights if partner data exists
        if partner_insights:
            st.subheader("Relationship Insights")
            
            # Mood correlation
            correlation = 0.72  # Sample correlation value
            
            st.markdown("### Mood Alignment")
            st.progress(correlation)
            
            if correlation > 0.7:
                st.success("Your moods are often aligned! When one of you is feeling good, the other tends to feel good too.")
            elif correlation > 0.4:
                st.info("Your moods show moderate alignment. Sometimes they match, sometimes they differ.")
            else:
                st.warning("Your moods often differ from each other. This is normal and can be an opportunity to support each other.")
            
            # Pattern insights
            st.markdown("### Patterns")
            
            # Sample patterns
            patterns = [
                "You both tend to have higher moods on weekends",
                "Your partner's mood tends to improve a day after yours improves",
                "You both frequently tag 'happy' on the same days"
            ]
            
            for pattern in patterns:
                st.markdown(f"- {pattern}")
    except Exception as e:
        st.error(f"Error loading mood insights: {str(e)}")
        st.info("This is a simulation. In a real environment, this would connect to the API.")

def display_mood_chart(user_moods, partner_moods, start_date):
    """Display mood rating chart"""
    st.subheader("Mood Trends")
    
    # Prepare data for chart
    chart_data = []
    
    # Add user moods to chart data
    for mood in user_moods:
        mood_date = datetime.strptime(mood['date'], '%Y-%m-%d').date()
        
        # Skip moods outside the selected date range
        if mood_date < start_date:
            continue
        
        chart_data.append({
            'date': mood_date,
            'rating': mood['rating'],
            'person': 'You'
        })
    
    # Add partner moods to chart data
    for mood in partner_moods:
        mood_date = datetime.strptime(mood['date'], '%Y-%m-%d').date()
        
        # Skip moods outside the selected date range
        if mood_date < start_date:
            continue
        
        chart_data.append({
            'date': mood_date,
            'rating': mood['rating'],
            'person': st.session_state.partner['name'] if st.session_state.partner else 'Partner'
        })
    
    if chart_data:
        # Convert to DataFrame for Altair
        df = pd.DataFrame(chart_data)
        
        # Create chart
        chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('rating:Q', title='Mood Rating', scale=alt.Scale(domain=[1, 10])),
            color=alt.Color('person:N', title='Person'),
            tooltip=['date:T', 'rating:Q', 'person:N']
        ).properties(
            width=600,
            height=300
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No mood data available for the selected time range.")

def display_mood_card(mood, is_partner=False, is_today=False):
    """Display a mood card"""
    rating = mood.get('rating', 0)
    
    # Define color based on rating
    if rating >= 8:
        color = "green"
        emoji = get_mood_emoji(rating)
    elif rating >= 6:
        color = "lightgreen"
        emoji = get_mood_emoji(rating)
    elif rating >= 4:
        color = "orange"
        emoji = get_mood_emoji(rating)
    else:
        color = "red"
        emoji = get_mood_emoji(rating)
    
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
            <div>
                <div style="font-size: 18px; font-weight: bold;">{rating}/10</div>
                <div style="font-size: 14px; color: #666;">{st.session_state.partner['name'] if is_partner else 'You'}</div>
            </div>
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

def get_mood_emoji(rating, selected=True):
    """Get emoji for mood rating"""
    # Emoji style
    style = "font-size: 24px; text-align: center; margin-bottom: 5px;"
    if selected:
        style += " opacity: 1.0;"
    else:
        style += " opacity: 0.5;"
    
    # Select emoji based on rating
    if rating == 1:
        emoji = "😭"
    elif rating == 2:
        emoji = "😢"
    elif rating == 3:
        emoji = "☹️"
    elif rating == 4:
        emoji = "🙁"
    elif rating == 5:
        emoji = "😐"
    elif rating == 6:
        emoji = "🙂"
    elif rating == 7:
        emoji = "😊"
    elif rating == 8:
        emoji = "😄"
    elif rating == 9:
        emoji = "😁"
    elif rating == 10:
        emoji = "🤩"
    else:
        emoji = "😐"
    
    return f'<div style="{style}">{emoji}</div>'