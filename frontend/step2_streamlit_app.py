import streamlit as st
import requests

st.set_page_config(page_title="AI Trainer", page_icon="💪", layout="centered")

st.title("💪 AI Personal Trainer Agent")
st.write("Fill the form and get your personalized gym plan instantly.")

goal = st.selectbox("🎯 Your Goal", ["Lose weight", "Build muscle", "Endurance", "Get toned"])
experience = st.selectbox("📊 Experience Level", ["Beginner", "Intermediate", Advanced"])
days = st.slider("📅 Training Days per Week", 1, 7, 3)
equipment = st.text_input("🏋️ Equipment Available")

if st.button("Generate Plan 🚀"):
    data = {
        "goal": goal,
        "experience": experience,
        "days": days,
        "equipment": equipment
    }

    response = requests.post("http://localhost:8000/generate_plan", json=data)

    if response.status_code == 200:
        st.success("Your Personalized Plan:")
        st.write(response.json()["plan"])
    else:
        st.error("Error connecting to backend.")
