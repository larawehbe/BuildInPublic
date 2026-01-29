import streamlit as st
import requests

st.set_page_config(page_title="AI Personal Trainer", page_icon="💪")
st.title("💪 Your AI Personal Trainer")

# Prepare backend API URLs
API_BASE = "http://localhost:8000"
PREFERENCES_API = f"{API_BASE}/update_preferences/"
CHAT_API = f"{API_BASE}/chat/"
HISTORY_API = f"{API_BASE}/chat_history/"

# Check if user is logged in
if "username" not in st.session_state or "session_id" not in st.session_state:
    st.error("⚠️ You must be logged in to access this page.")
    st.switch_page("auth.py")

# Prepare chat history container
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create tabs
tab_preferences, tab_chat = st.tabs(["⚙️ Preferences", "💬 Chatbot"])

# First tab: Preferences
with tab_preferences:
    st.subheader("⚙️ Personal Preferences")

    with st.form("preferences_form"):
        age = st.number_input("👶 Age", min_value=18, max_value=60, value=20)
        gender = st.radio("👤 Gender", ["Male", "Female"])
        weight = st.number_input("🏋️ Weight (kg)",
                                 min_value=30,
                                 max_value=150,
                                 value=70)
        height = st.number_input("📏 Height (cm)",
                                 min_value=140,
                                 max_value=220,
                                 value=170)
        goal = st.text_input("🎯 Fitness goal",
                             placeholder="Build muscle, lose fat, stay fit...")

        experience = st.selectbox("🔥 Experience level",
                                  ["Beginner", "Intermediate", "Advanced"])

        tone = st.selectbox("🗣️ Coaching tone",
                            ["Motivational", "Strict", "Friendly", "Neutral"])

        days_per_week = st.slider("📅 Training days per week", 1, 7, 4)

        equipment = st.text_area(
            "🏋️ Available equipment",
            placeholder="Dumbbells, resistance bands, gym access...")

        save_preferences = st.form_submit_button("💾 Save Preferences")

    # Save preferences to backend
    if save_preferences:
        if not goal or not equipment:
            st.warning("⚠️ Please fill in all required fields.")
        else:
            with st.spinner("Saving your preferences..."):
                response = requests.post(PREFERENCES_API,
                                         json={
                                             "username":
                                             st.session_state.username,
                                             "goal": goal,
                                             "experience": experience,
                                             "tone": tone,
                                             "days_per_week": days_per_week,
                                             "equipment": equipment,
                                             "gender": gender,
                                             "age": age,
                                             "weight": weight,
                                             "height": height
                                         })

                if response.status_code == 200:
                    st.success("✅ Preferences saved successfully!")
                else:
                    st.error("❌ Failed to save preferences.")

# Second tab: Chatbot
with tab_chat:
    st.subheader("💬 Chat with your AI Trainer")

    # Load chat history from backend
    if not st.session_state.messages:
        history_response = requests.get(
            f"{HISTORY_API}/{st.session_state.username}")

        if history_response.status_code == 200:
            st.session_state.messages = history_response.json()["messages"]

    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(
                    f"<div style='background-color:#7e57c2; padding:10px; border-radius:10px; color:black;'>"
                    f"{msg['content']}</div>",
                    unsafe_allow_html=True)
        else:
            with st.chat_message("assistant"):
                st.markdown(
                    f"<div style='background-color:#42a5f5; padding:10px; border-radius:10px; color:black;'>"
                    f"{msg['content']}</div>",
                    unsafe_allow_html=True)

    # Chat input
    col1, col2 = st.columns([5, 1])

    with col1:
        user_input = st.text_input(
            "Type your message",
            placeholder="Ask about workouts, nutrition, recovery...")

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
                unsafe_allow_html=True)

        # Call backend
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                st.write("⏳ Generating response...")
                response = requests.post(CHAT_API,
                                         json={
                                             "username":
                                             st.session_state.username,
                                             "message": user_input
                                         })
                st.write(response.status_code)
                if response.status_code == 200:
                    assistant_reply = response.json()["response"]
                else:
                    assistant_reply = "❌ Something went wrong."

                st.markdown(
                    f"<div style='background-color:#42a5f5; padding:10px; border-radius:10px; color:white;'>"
                    f"{assistant_reply}</div>",
                    unsafe_allow_html=True)

        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_reply
        })
