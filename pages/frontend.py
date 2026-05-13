import os
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Personal Trainer")
st.title("Your AI Personal Trainer")

# Prepare backend API URLs
API_BASE = os.environ.get("API_BASE", "http://localhost:8001").rstrip("/")
PREFERENCES_API = f"{API_BASE}/update_preferences/"
CHAT_API = f"{API_BASE}/chat/"
HISTORY_API = f"{API_BASE}/chat_history/"
ANALYZE_API = f"{API_BASE}/analyze_image/"

# Check if user is logged in
if "username" not in st.session_state or "session_id" not in st.session_state:
    st.error("You must be logged in to access this page.")
    st.switch_page("app.py")

# Prepare chat history container
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create tabs
tab_preferences, tab_chat = st.tabs(["Preferences", "Chatbot"])

# First tab: Preferences
with tab_preferences:
    st.subheader("Personal Preferences")

    with st.form("preferences_form"):
        age = st.number_input("Age", min_value=18, max_value=60, value=20)
        gender = st.radio("Gender", ["Male", "Female"])
        weight = st.number_input("Weight (kg)",
                                 min_value=30,
                                 max_value=150,
                                 value=70)
        height = st.number_input("Height (cm)",
                                 min_value=140,
                                 max_value=220,
                                 value=170)
        goal = st.text_input("Fitness goal",
                             placeholder="Build muscle, lose fat, stay fit...")

        experience = st.selectbox("Experience level",
                                  ["Beginner", "Intermediate", "Advanced"])

        tone = st.selectbox("Coaching tone",
                            ["Motivational", "Strict", "Friendly", "Neutral"])

        days_per_week = st.slider("Training days per week", 1, 7, 4)

        equipment = st.text_area(
            "Available equipment",
            placeholder="Dumbbells, resistance bands, gym access...")

        save_preferences = st.form_submit_button("Save Preferences")

    # Save preferences to backend
    if save_preferences:
        if not goal or not equipment:
            st.warning("Please fill in all required fields.")
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
                    st.success("Preferences saved successfully!")
                else:
                    st.error("Failed to save preferences.")

# Second tab: Chatbot
with tab_chat:
    st.subheader("Chat with your AI Trainer")

    # Image upload section
    with st.expander("Upload an exercise image for analysis"):
        uploaded_file = st.file_uploader("Choose an exercise image", type=["jpg", "jpeg", "png", "webp"])

        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded image")

            if st.button("Analyze Exercise"):
                with st.spinner("Analyzing your exercise image..."):
                    response = requests.post(
                        ANALYZE_API,
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                        data={"username": st.session_state.username},
                    )

                if response.status_code == 200:
                    analysis = response.json()["analysis"]
                    st.session_state.messages.append({"role": "user", "content": "[Uploaded an exercise image for analysis]"})
                    st.session_state.messages.append({"role": "assistant", "content": analysis})
                    st.rerun()
                else:
                    st.error("Failed to analyze the image. Please try again.")

    # Document upload section (PDF/DOCX)
    with st.expander("Upload your coach's fitness plan (PDF/DOCX)"):
        doc_file = st.file_uploader("Choose a fitness plan document", type=["pdf", "docx", "doc"])

        if doc_file is not None:
            if st.button("Upload & Sync Plan"):
                with st.spinner("Processing your fitness plan..."):
                    mime_type = "application/pdf" if doc_file.name.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    response = requests.post(
                        f"{API_BASE}/upload_document/",
                        files={"file": (doc_file.name, doc_file.getvalue(), mime_type)},
                        data={"username": st.session_state.username},
                    )

                if response.status_code == 200:
                    body = response.json()
                    st.success(
                        f"Fitness plan synced! Extracted {body.get('text_length', 0)} chars "
                        f"into {body.get('chunks_created', 0)} chunks. You can now ask questions about it."
                    )
                    st.session_state.messages.append({"role": "user", "content": f"[Uploaded a fitness plan document: {doc_file.name}]"})
                    st.session_state.messages.append({"role": "assistant", "content": f"I've received your fitness plan ({doc_file.name})! I'll use it as a reference for your workouts, keeping in mind your preferences and any constraints like no gym access."})
                    st.rerun()
                else:
                    try:
                        detail = response.json().get("detail", response.text)
                    except Exception:
                        detail = response.text
                    st.error(f"Failed to upload the document: {detail}")

    # Load chat history from backend
    if not st.session_state.messages:
        history_response = requests.get(
            f"{HISTORY_API}/{st.session_state.username}")

        if history_response.status_code == 200:
            st.session_state.messages = history_response.json()["messages"]

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

user_input = st.chat_input("Ask about workouts, nutrition, recovery...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking..."):
        response = requests.post(CHAT_API,
                                 json={
                                     "username": st.session_state.username,
                                     "message": user_input
                                 })
        if response.status_code == 200:
            assistant_reply = response.json()["response"]
        else:
            assistant_reply = "Something went wrong."

    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_reply
    })
    st.rerun()
