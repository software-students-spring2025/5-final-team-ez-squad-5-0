"""
Prompts component for the Together web application
"""
import os
import streamlit as st
import requests
from datetime import datetime

# API URL
API_URL = os.environ.get('API_URL', 'http://localhost:5000')

def display_prompts():
    """Display conversation prompts interface"""
    st.title("Conversation Starters")
    
    # Create tabs for different prompt categories
    tabs = st.tabs(["Daily", "Fun", "Deep", "Growth", "History", "All Prompts"])
    
    # Daily prompts
    with tabs[0]:
        display_daily_prompt()
    
    # Fun prompts
    with tabs[1]:
        display_prompt_category("fun", "Fun & Playful Prompts", "Lighthearted questions to bring joy and laughter")
    
    # Deep prompts
    with tabs[2]:
        display_prompt_category("deep", "Deep Connection Prompts", "Thoughtful questions to deepen your understanding of each other")
    
    # Growth prompts
    with tabs[3]:
        display_prompt_category("growth", "Growth & Future Prompts", "Questions about your future and growth as individuals and as a couple")
    
    # History prompts
    with tabs[4]:
        display_prompt_category("history", "Relationship History Prompts", "Reflect on your journey together and cherish memories")
    
    # All prompts
    with tabs[5]:
        display_all_prompts()

def display_daily_prompt():
    """Display daily conversation prompt"""
    st.header("Today's Prompt")
    
    try:
        # In a real app, we would make an API call to get the daily prompt
        # response = requests.get(
        #     f"{API_URL}/api/prompts/daily",
        #     headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        # )
        
        # For this simulation, we'll use a sample prompt
        prompt = {
            "prompt_id": "daily-123",
            "content": "What's one small thing I've done recently that made you feel appreciated?",
            "category": "daily",
            "answered": False
        }
        
        display_prompt_card(prompt)
        
        # If prompt hasn't been answered, show response form
        if not prompt.get("answered"):
            with st.form(f"response_form_{prompt['prompt_id']}"):
                response_text = st.text_area("Your Response", height=100)
                submit = st.form_submit_button("Share")
                
                if submit:
                    if not response_text:
                        st.error("Please enter your response")
                    else:
                        # In a real app, we would make an API call to submit the response
                        # response = requests.post(
                        #     f"{API_URL}/api/prompts/{prompt['prompt_id']}/responses",
                        #     headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                        #     json={"content": response_text}
                        # )
                        
                        # For this simulation, we'll show a success message
                        st.success("Response shared with your partner!")
                        st.experimental_rerun()
    except Exception as e:
        st.error(f"Error loading daily prompt: {str(e)}")
        st.info("This is a simulation. In a real environment, this would connect to the API.")

def display_prompt_category(category, title, description):
    """Display prompts for a specific category"""
    st.header(title)
    st.markdown(description)
    
    try:
        # In a real app, we would make an API call to get prompts for this category
        # response = requests.get(
        #     f"{API_URL}/api/prompts/?category={category}",
        #     headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        # )
        
        # For this simulation, we'll use sample prompts
        prompts = []
        if category == "fun":
            prompts = [
                {
                    "prompt_id": "fun-1",
                    "content": "If we could teleport anywhere for a date night right now, where would you choose and why?",
                    "category": "fun",
                    "answered": False
                },
                {
                    "prompt_id": "fun-2",
                    "content": "What's a song that always makes you think of me?",
                    "category": "fun",
                    "answered": True
                }
            ]
        elif category == "deep":
            prompts = [
                {
                    "prompt_id": "deep-1",
                    "content": "What's something you've been afraid to tell me, but want me to know?",
                    "category": "deep",
                    "answered": False
                },
                {
                    "prompt_id": "deep-2",
                    "content": "When do you feel most connected to me?",
                    "category": "deep",
                    "answered": False
                }
            ]
        elif category == "growth":
            prompts = [
                {
                    "prompt_id": "growth-1",
                    "content": "What's one way we've grown together in the past year?",
                    "category": "growth",
                    "answered": False
                },
                {
                    "prompt_id": "growth-2",
                    "content": "What's a goal you'd like us to work toward together?",
                    "category": "growth",
                    "answered": False
                }
            ]
        elif category == "history":
            prompts = [
                {
                    "prompt_id": "history-1",
                    "content": "What moment in our relationship do you find yourself thinking about most often?",
                    "category": "history",
                    "answered": False
                },
                {
                    "prompt_id": "history-2",
                    "content": "When did you first realize this relationship was special?",
                    "category": "history",
                    "answered": True
                }
            ]
        
        # Display prompts
        for prompt in prompts:
            display_prompt_card(prompt)
    except Exception as e:
        st.error(f"Error loading prompts: {str(e)}")
        st.info("This is a simulation. In a real environment, this would connect to the API.")

def display_all_prompts():
    """Display all prompts with filters"""
    st.header("All Prompts")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        category_filter = st.selectbox(
            "Category",
            options=["All", "Fun", "Deep", "Growth", "History", "Daily"],
            index=0,
            key="all_category_filter"
        )
    
    with col2:
        answered_filter = st.selectbox(
            "Status",
            options=["All", "Answered", "Unanswered"],
            index=0,
            key="all_answered_filter"
        )
    
    try:
        # In a real app, we would make an API call to get prompts with filters
        # params = {}
        # if category_filter != "All":
        #     params["category"] = category_filter.lower()
        # if answered_filter != "All":
        #     params["completed"] = answered_filter == "Answered"
        # response = requests.get(
        #     f"{API_URL}/api/prompts/",
        #     headers={"Authorization": f"Bearer {st.session_state.access_token}"},
        #     params=params
        # )
        
        # For this simulation, we'll use sample prompts from all categories
        all_prompts = [
            {"prompt_id": "fun-1", "content": "If we could teleport anywhere for a date night right now, where would you choose and why?", "category": "fun", "answered": False},
            {"prompt_id": "deep-1", "content": "What's something you've been afraid to tell me, but want me to know?", "category": "deep", "answered": False},
            {"prompt_id": "growth-1", "content": "What's one way we've grown together in the past year?", "category": "growth", "answered": False},
            {"prompt_id": "history-1", "content": "What moment in our relationship do you find yourself thinking about most often?", "category": "history", "answered": False},
            {"prompt_id": "fun-2", "content": "What's a song that always makes you think of me?", "category": "fun", "answered": True},
            {"prompt_id": "history-2", "content": "When did you first realize this relationship was special?", "category": "history", "answered": True}
        ]
        
        # Apply filters
        filtered_prompts = all_prompts
        if category_filter != "All":
            filtered_prompts = [p for p in filtered_prompts if p["category"].lower() == category_filter.lower()]
        if answered_filter != "All":
            filtered_prompts = [p for p in filtered_prompts if p["answered"] == (answered_filter == "Answered")]
        
        # Display prompts
        for prompt in filtered_prompts:
            display_prompt_card(prompt)
            
        if not filtered_prompts:
            st.info("No prompts match your filters.")
    except Exception as e:
        st.error(f"Error loading prompts: {str(e)}")
        st.info("This is a simulation. In a real environment, this would connect to the API.")

def display_prompt_card(prompt):
    """Display a prompt card with response option"""
    # Create a card for the prompt
    st.markdown(
        f"""
        <div style="
            padding: 15px;
            border-radius: 10px;
            background-color: #f0f8ff;
            border: 1px solid #add8e6;
            margin-bottom: 15px;
        ">
            <div style="font-style: italic; font-weight: bold;">{prompt['content']}</div>
            <div style="font-size: 12px; color: #666; margin-top: 5px;">Category: {prompt['category'].capitalize()}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Check if prompt has been answered
    if prompt.get("answered"):
        st.success("You've both responded to this prompt!")
        
        # Show responses
        with st.expander("View Responses"):
            # In a real app, we would make an API call to get responses
            # response = requests.get(
            #     f"{API_URL}/api/prompts/{prompt['prompt_id']}/responses",
            #     headers={"Authorization": f"Bearer {st.session_state.access_token}"}
            # )
            
            # For this simulation, we'll use sample responses
            responses = [
                {
                    "user_id": st.session_state.user['user_id'],
                    "user_name": st.session_state.user['name'],
                    "content": "I really love our weekend morning walks. They're simple but those moments of just talking and enjoying nature together are special to me.",
                    "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
                    "is_partner": False
                }
            ]
            
            if st.session_state.partner:
                responses.append({
                    "user_id": st.session_state.partner['user_id'],
                    "user_name": st.session_state.partner['name'],
                    "content": "I think the small surprise gifts you leave for me to find throughout the week. It shows you're thinking of me even during busy days.",
                    "created_at": datetime.now().isoformat(),
                    "is_partner": True
                })
            
            for response in responses:
                # Format date
                response_date = datetime.fromisoformat(response['created_at'].replace('Z', '+00:00') if 'Z' in response['created_at'] else response['created_at'])
                date_display = response_date.strftime("%b %d, %Y at %I:%M %p")
                
                # Different styling for user vs partner
                bg_color = "#e6f7ff" if response.get('is_partner') else "#f0f0f0"
                border_color = "#0066cc" if response.get('is_partner') else "#888"
                
                st.markdown(
                    f"""
                    <div style="
                        padding: 10px 15px;
                        border-radius: 10px;
                        background-color: {bg_color};
                        margin-bottom: 10px;
                        border-left: 3px solid {border_color};
                    ">
                        <div style="font-weight: bold; font-size: 14px;">{response['user_name']}</div>
                        <div style="margin: 5px 0;">{response['content']}</div>
                        <div style="font-size: 12px; color: #777; text-align: right;">{date_display}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        # Show response form if prompt hasn't been answered
        with st.form(f"response_form_{prompt['prompt_id']}"):
            response_text = st.text_area("Your Response", height=100, key=f"response_{prompt['prompt_id']}")
            submit = st.form_submit_button("Share Response")
            
            if submit:
                if not response_text:
                    st.error("Please enter your response")
                else:
                    # In a real app, we would make an API call to submit the response
                    # response = requests.post(
                    #     f"{API_URL}/api/prompts/{prompt['prompt_id']}/responses",
                    #     headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                    #     json={"content": response_text}
                    # )
                    
                    # For this simulation, we'll show a success message
                    st.success("Response shared with your partner!")
                    prompt["answered"] = True
                    st.experimental_rerun()