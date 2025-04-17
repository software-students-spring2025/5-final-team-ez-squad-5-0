"""
Goals component for the Together web application
"""
import os
import streamlit as st
import requests
from datetime import datetime, timedelta

# API URL
API_URL = os.environ.get('API_URL', 'http://localhost:5000')

def display_goals():
    """Display goals interface"""
    st.title("Goals")
    
    # Create tabs for different goal views
    tab1, tab2, tab3 = st.tabs(["Active Goals", "Create Goal", "Completed Goals"])
    
    with tab1:
        display_active_goals()
    
    with tab2:
        create_goal_form()
    
    with tab3:
        display_completed_goals()

def display_active_goals():
    """Display active goals"""
    st.header("Active Goals")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        category_filter = st.selectbox(
            "Category",
            options=["All", "Relationship", "Personal", "Shared", "Other"],
            index=0
        )
    
    # Build filter parameters
    params = {}
    if category_filter != "All":
        params["category"] = category_filter.lower()
    
    params["completed"] = False
    
    try:
        # In a real app, we would fetch goals from the API
        # For simulation, create sample goals
        active_goals = [
            {
                "goal_id": "goal1",
                "title": "Weekly Date Night",
                "description": "Have a dedicated date night every week to strengthen our connection",
                "category": "relationship",
                "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
                "progress": 50,
                "completed": False,
                "milestones": [
                    {
                        "milestone_id": "m1",
                        "title": "Schedule recurring calendar event",
                        "completed": True
                    },
                    {
                        "milestone_id": "m2",
                        "title": "Create list of date ideas",
                        "completed": True
                    },
                    {
                        "milestone_id": "m3",
                        "title": "Complete first month of weekly dates",
                        "completed": False
                    },
                    {
                        "milestone_id": "m4",
                        "title": "Reflect on which dates were most enjoyable",
                        "completed": False
                    }
                ]
            },
            {
                "goal_id": "goal2",
                "title": "Learn to Cook Together",
                "description": "Take an online cooking class together and learn to make 5 new dishes",
                "category": "shared",
                "deadline": (datetime.now() + timedelta(days=60)).isoformat(),
                "progress": 20,
                "completed": False,
                "milestones": [
                    {
                        "milestone_id": "m5",
                        "title": "Find and sign up for cooking class",
                        "completed": True
                    },
                    {
                        "milestone_id": "m6",
                        "title": "Complete first recipe together",
                        "completed": False
                    },
                    {
                        "milestone_id": "m7",
                        "title": "Learn 3 more recipes",
                        "completed": False
                    },
                    {
                        "milestone_id": "m8",
                        "title": "Host dinner party with new skills",
                        "completed": False
                    }
                ]
            },
            {
                "goal_id": "goal3",
                "title": "Read 10 Books This Year",
                "description": "Personal goal to read more fiction and non-fiction books",
                "category": "personal",
                "deadline": (datetime.now() + timedelta(days=120)).isoformat(),
                "progress": 30,
                "completed": False,
                "private": True,
                "milestones": [
                    {
                        "milestone_id": "m9",
                        "title": "Create reading list",
                        "completed": True
                    },
                    {
                        "milestone_id": "m10",
                        "title": "Read first 3 books",
                        "completed": True
                    },
                    {
                        "milestone_id": "m11",
                        "title": "Read next 3 books",
                        "completed": False
                    },
                    {
                        "milestone_id": "m12",
                        "title": "Read final 4 books",
                        "completed": False
                    }
                ]
            }
        ]
        
        # Filter goals based on category
        if category_filter != "All":
            filtered_goals = [g for g in active_goals if g["category"] == category_filter.lower()]
        else:
            filtered_goals = active_goals
        
        # Display goals
        if not filtered_goals:
            st.info(f"No active goals found for the selected category.")
        else:
            for goal in filtered_goals:
                display_goal_card(goal)
    except Exception as e:
        st.error(f"Error loading goals: {str(e)}")
        st.info("This is a simulation. In a real environment, this would connect to the API.")

def display_completed_goals():
    """Display completed goals"""
    st.header("Completed Goals")
    
    try:
        # In a real app, we would fetch completed goals from the API
        # For simulation, create sample completed goals
        completed_goals = [
            {
                "goal_id": "goal4",
                "title": "Create Shared Budget",
                "description": "Set up a shared budget and financial planning system",
                "category": "relationship",
                "completed": True,
                "completion_date": (datetime.now() - timedelta(days=15)).isoformat(),
                "progress": 100
            },
            {
                "goal_id": "goal5",
                "title": "Run a Half Marathon",
                "description": "Train for and complete a half marathon",
                "category": "personal",
                "completed": True,
                "completion_date": (datetime.now() - timedelta(days=45)).isoformat(),
                "progress": 100,
                "private": True
            }
        ]
        
        # Display goals
        if not completed_goals:
            st.info("No completed goals found.")
        else:
            for goal in completed_goals:
                display_goal_card(goal, show_milestones=False)
    except Exception as e:
        st.error(f"Error loading completed goals: {str(e)}")
        st.info("This is a simulation. In a real environment, this would connect to the API.")

def create_goal_form():
    """Display form to create a new goal"""
    st.header("Create New Goal")
    
    with st.form("create_goal_form", clear_on_submit=True):
        title = st.text_input("Goal Title")
        
        description = st.text_area("Description", help="What do you want to achieve and why?")
        
        category = st.selectbox(
            "Category",
            options=["Relationship", "Personal", "Shared", "Other"],
            index=0
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            has_deadline = st.checkbox("Set Deadline", value=True)
        
        with col2:
            if has_deadline:
                deadline = st.date_input("Deadline", value=datetime.now().date() + timedelta(days=30))
        
        # Milestones
        st.subheader("Milestones")
        st.markdown("Break down your goal into smaller steps")
        
        milestone1 = st.text_input("Milestone 1")
        milestone2 = st.text_input("Milestone 2")
        milestone3 = st.text_input("Milestone 3")
        milestone4 = st.text_input("Milestone 4 (Optional)")
        milestone5 = st.text_input("Milestone 5 (Optional)")
        
        # Privacy settings
        private = st.checkbox("Private Goal (only visible to you)", value=(category.lower() == "personal"))
        
        # Submit button
        submit = st.form_submit_button("Create Goal")
        
        if submit:
            if not title:
                st.error("Please enter a goal title")
                return
            
            if not description:
                st.error("Please enter a goal description")
                return
            
            # Collect milestones
            milestones = []
            if milestone1:
                milestones.append({"title": milestone1, "completed": False})
            if milestone2:
                milestones.append({"title": milestone2, "completed": False})
            if milestone3:
                milestones.append({"title": milestone3, "completed": False})
            if milestone4:
                milestones.append({"title": milestone4, "completed": False})
            if milestone5:
                milestones.append({"title": milestone5, "completed": False})
            
            # Prepare goal data
            goal_data = {
                "title": title,
                "description": description,
                "category": category.lower(),
                "private": private,
                "completed": False,
                "progress": 0,
                "milestones": milestones
            }
            
            # Add deadline if set
            if has_deadline:
                goal_data["deadline"] = deadline.isoformat()
            
            try:
                # In a real app, we would create the goal via API
                # For simulation, show success message
                st.success("Goal created successfully!")
                
                # Display the new goal
                display_goal_card(goal_data)
            except Exception as e:
                st.error(f"Error creating goal: {str(e)}")

def display_goal_card(goal, show_milestones=True):
    """Display a goal card"""
    # Create expandable container for the goal
    with st.expander(f"**{goal['title']}**", expanded=True):
        # Goal details
        st.markdown(f"**Category:** {goal['category'].capitalize()}")
        st.markdown(f"**Description:** {goal['description']}")
        
        # Progress bar
        progress = goal.get('progress', 0)
        st.progress(progress / 100)
        st.markdown(f"**Progress:** {progress}%")
        
        # Deadline
        if goal.get('deadline'):
            deadline_date = datetime.fromisoformat(goal['deadline'].replace('Z', '+00:00') if 'Z' in goal['deadline'] else goal['deadline']).date()
            today = datetime.now().date()
            days_left = (deadline_date - today).days
            
            if days_left > 0:
                st.markdown(f"**Deadline:** {deadline_date.strftime('%B %d, %Y')} ({days_left} days left)")
            elif days_left == 0:
                st.markdown(f"**Deadline:** Today!")
            else:
                st.markdown(f"**Deadline:** {deadline_date.strftime('%B %d, %Y')} (Overdue by {abs(days_left)} days)")
        
        # Completion date for completed goals
        if goal.get('completed') and goal.get('completion_date'):
            completion_date = datetime.fromisoformat(goal['completion_date'].replace('Z', '+00:00') if 'Z' in goal['completion_date'] else goal['completion_date']).date()
            st.markdown(f"**Completed on:** {completion_date.strftime('%B %d, %Y')}")
        
        # Privacy indicator
        if goal.get('private'):
            st.markdown("🔒 Private goal (only visible to you)")
        
        # Milestones section
        if show_milestones and goal.get('milestones'):
            st.markdown("---")
            st.markdown("### Milestones")
            
            for i, milestone in enumerate(goal['milestones']):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Checkbox for milestone completion
                    completed = st.checkbox(
                        milestone['title'],
                        value=milestone.get('completed', False),
                        key=f"milestone_{goal['goal_id']}_{i}"
                    )
                    
                    # In a real app, we would update the milestone status via API if changed
                
                with col2:
                    if not goal.get('completed'):
                        # Delete milestone button
                        if st.button("Delete", key=f"delete_milestone_{goal['goal_id']}_{i}"):
                            st.warning("This is a simulation. In a real app, this would delete the milestone.")
        
        # Action buttons
        if not goal.get('completed'):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Edit goal button
                if st.button("Edit Goal", key=f"edit_{goal['goal_id']}"):
                    st.session_state.edit_goal = goal
                    st.experimental_rerun()
            
            with col2:
                # Add milestone button
                if st.button("Add Milestone", key=f"add_milestone_{goal['goal_id']}"):
                    st.session_state.add_milestone_goal_id = goal['goal_id']
                    st.experimental_rerun()
            
            with col3:
                # Complete goal button
                if st.button("Mark Complete", key=f"complete_{goal['goal_id']}"):
                    # In a real app, we would update the goal via API
                    st.success("Goal marked as complete!")
        else:
            # Delete completed goal button
            if st.button("Delete Goal", key=f"delete_{goal['goal_id']}"):
                # In a real app, we would delete the goal via API
                st.success("Goal deleted!")
