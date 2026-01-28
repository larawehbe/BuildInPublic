# import streamlit as st
# import requests
# import os

# st.set_page_config(page_title="AI Personal Trainer", page_icon="💪")
# st.title("💪 Your AI Personal Trainer")
# st.write(
#     "Answer a few questions and get your personalized gym plan instantly.")

# with st.form("trainer_form"):
#     goal = st.text_input(
#         "🎯 What's your fitness goal? (e.g. build muscle, lose fat, stay fit)")
#     experience = st.selectbox("🔥 Your experience level:",
#                               ["Beginner", "Intermediate", "Advanced"])
#     days_per_week = st.slider("📅 How many days per week can you train?", 1, 7,
#                               4)
#     equipment = st.text_area(
#         "🏋️ What equipment do you have? (e.g. dumbbells, resistance bands, gym access)"
#     )
#     submitted = st.form_submit_button("Generate Plan 🚀")

# API_URL = "http://buildinpublic.ranaalmaaz55.repl.co/generate_plan/"

# if submitted:
#     if not goal or not equipment:
#         st.warning("⚠️ Please fill in all fields before submitting.")
#     else:
#         with st.spinner("Generating your gym plan..."):
#             try:
#                 response = requests.post(API_URL,
#                                          json={
#                                              "goal": goal,
#                                              "experience": experience,
#                                              "days_per_week": days_per_week,
#                                              "equipment": equipment
#                                          })

#                 if response.status_code == 200:
#                     plan = response.json()["gym_plan"]
#                     st.success("🏋️ Here's your personalized plan:")
#                     st.markdown(plan)
#                 else:
#                     st.error("❌ Something went wrong. Please try again.")
#             except requests.exceptions.ConnectionError:
#                 st.error(
#                     "❌ Could not connect to the backend. Please make sure the server is running."
#                 )


import streamlit as st
import requests
import os

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="AI Personal Trainer", page_icon="💪")
st.title("💪 Your AI Personal Trainer")

# -------------------------------
# Backend URLs
# -------------------------------
API_BASE = "http://localhost:8000"
# API_BASE = "https://buildinpublic.ranaalmaaz55.repl.co"
PREFERENCES_API = f"{API_BASE}/update_preferences/"
CHAT_API = f"{API_BASE}/chat/"
HISTORY_API = f"{API_BASE}/chat_history/"

# -------------------------------
# Session guards
# -------------------------------
if "username" not in st.session_state or "session_id" not in st.session_state:
    st.error("⚠️ You must be logged in to access this page.")
    st.switch_page("auth.py")

# -------------------------------
# UI state
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# Tabs
# -------------------------------
tab_preferences, tab_chat = st.tabs(["⚙️ Preferences", "💬 Chatbot"])

# =====================================================
# TAB 1: USER PREFERENCES
# =====================================================
with tab_preferences:
    st.subheader("⚙️ Personal Preferences")

    with st.form("preferences_form"):
        goal = st.text_input(
            "🎯 Fitness goal",
            placeholder="Build muscle, lose fat, stay fit..."
        )

        experience = st.selectbox(
            "🔥 Experience level",
            ["Beginner", "Intermediate", "Advanced"]
        )

        tone = st.selectbox(
            "🗣️ Coaching tone",
            ["Motivational", "Strict", "Friendly", "Neutral"]
        )

        days_per_week = st.slider(
            "📅 Training days per week",
            1, 7, 4
        )

        equipment = st.text_area(
            "🏋️ Available equipment",
            placeholder="Dumbbells, resistance bands, gym access..."
        )

        save_preferences = st.form_submit_button("💾 Save Preferences")

    if save_preferences:
        if not goal or not equipment:
            st.warning("⚠️ Please fill in all required fields.")
        else:
            with st.spinner("Saving your preferences..."):
                response = requests.post(
                    PREFERENCES_API,
                    json={
                        "username": st.session_state.username,
                        "goal": goal,
                        "experience": experience,
                        "tone": tone,
                        "days_per_week": days_per_week,
                        "equipment": equipment,
                    }
                )

                if response.status_code == 200:
                    st.success("✅ Preferences saved successfully!")
                else:
                    st.error("❌ Failed to save preferences.")

# =====================================================
# TAB 2: CHATBOT
# =====================================================
with tab_chat:
    st.subheader("💬 Chat with your AI Trainer")

    # -------------------------------
    # Load previous messages once
    # -------------------------------
    if not st.session_state.messages:
        history_response = requests.get(f"{HISTORY_API}/{st.session_state.username}")

        if history_response.status_code == 200:
            st.session_state.messages = history_response.json()["messages"]

    # -------------------------------
    # Display chat history
    # -------------------------------
    for msg in st.session_state.messages:
        if msg.role == "user":
            with st.chat_message("user"):
                st.markdown(
                    f"<div style='background-color:#7e57c2; padding:10px; border-radius:10px; color:black;'>"
                    f"{msg.content}</div>",
                    unsafe_allow_html=True
                )
        else:
            with st.chat_message("assistant"):
                st.markdown(
                    f"<div style='background-color:#42a5f5; padding:10px; border-radius:10px; color:black;'>"
                    f"{msg.content}</div>",
                    unsafe_allow_html=True
                )

    # -------------------------------
    # Input + Send button
    # -------------------------------
    col1, col2 = st.columns([5, 1])

    with col1:
        user_input = st.text_input(
            "Type your message",
            placeholder="Ask about workouts, nutrition, recovery..."
        )

    with col2:
        send_clicked = st.button("Send ➤")

    if send_clicked and user_input:
        # Show user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(
                f"<div style='background-color:#7e57c2; padding:10px; border-radius:10px; color:white;'>"
                f"{user_input}</div>",
                unsafe_allow_html=True
            )

        # Call backend
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = requests.post(
                    CHAT_API,
                    json={
                        "username": st.session_state.username,
                        "message": user_input,
                        "messages": st.session_state.messages
                    }
                )

                if response.status_code == 200:
                    assistant_reply = response.json()["response"]
                else:
                    assistant_reply = "❌ Something went wrong."

                st.markdown(
                    f"<div style='background-color:#42a5f5; padding:10px; border-radius:10px; color:white;'>"
                    f"{assistant_reply}</div>",
                    unsafe_allow_html=True
                )

        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_reply
        })
