import streamlit as st
import requests

# --- Streamlit page setup ---
st.set_page_config(page_title="AI Personal Trainer 💪", page_icon="🏋️")
st.title("💪 Your AI Personal Trainer")
st.write("Answer a few questions and get your personalized gym plan instantly.")

# --- User input form ---
with st.form("trainer_form"):
    goal = st.text_input("🎯 What’s your fitness goal? (e.g. build muscle, lose fat, stay fit)")
    experience = st.selectbox("🔥 Your experience level:", ["Beginner", "Intermediate", "Advanced"])
    days_per_week = st.slider("📅 How many days per week can you train?", 1, 7, 4)
    equipment = st.text_area("🏋️ What equipment do you have? (e.g. dumbbells, resistance bands, gym access)")
    submitted = st.form_submit_button("Generate Plan 🚀")

# --- Backend API URL ---
API_URL = "http://127.0.0.1:8000/generate_plan/"  # update if deployed

# --- Call the FastAPI backend ---
if submitted:
    if not goal or not equipment:
        st.warning("⚠️ Please fill in all fields before submitting.")
    else:
        with st.spinner("Generating your gym plan..."):
            response = requests.post(API_URL, json={
                "goal": goal,
                "experience": experience,
                "days_per_week": days_per_week,
                "equipment": equipment
            })

            if response.status_code == 200:
                plan = response.json()["gym_plan"]
                st.success("🏋️ Here’s your personalized plan:")
                st.markdown(plan)
            else:
                st.error("❌ Something went wrong. Make sure the FastAPI server is running.")
