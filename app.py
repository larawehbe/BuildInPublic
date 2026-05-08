import os
import streamlit as st
import requests
import uuid
from dotenv import load_dotenv

load_dotenv()
print(f'API_BASE: {os.environ.get("API_BASE")}')  
API_BASE = os.environ.get("API_BASE", "http://localhost:8001").rstrip("/")

st.title("Login/Signup")
username = st.text_input("Username")

if "session_id" in st.session_state and "username" in st.session_state:
  st.switch_page("pages/frontend.py")

# Logging in
if st.button("Login"):
  if username:
    st.session_state.session_id = str(uuid.uuid4())
    response = requests.post(f"{API_BASE}/login/",
                             json={
                                 "username": username,
                                 "session_id": st.session_state.session_id
                             })

    if response.status_code == 200:
      if response.json()["exists"]:
        st.session_state.username = username
        st.success("Logged in successfully!")
        st.switch_page("pages/frontend.py")
      else:
        st.warning("User not found. Please sign up.")
    else:
      st.error("Failed to connect to the server.")
  else:
    st.error("Username is required")

# Signing up
if st.button("Signup"):
  if username:
    st.session_state.session_id = str(uuid.uuid4())
    response = requests.post(f"{API_BASE}/signup/",
                             json={
                                 "username": username,
                                 "session_id": st.session_state.session_id
                             })
    if response.status_code == 200:
      if response.json()["exists"]:
        st.warning(
            "Username already exists. Please login or choose a different username."
        )
      else:
        st.session_state.username = username
        st.success("Signed up successfully!")
        st.switch_page("pages/frontend.py")
    else:
      st.error("Failed to connect to the server.")
  else:
    st.error("Username is required")
