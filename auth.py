import streamlit as st
import requests
import uuid

st.title("Login/Signup")
username = st.text_input("Username")

if "session_id" in st.session_state and "username" in st.session_state:
      st.switch_page("pages/frontend.py")


if st.button("Login"):
   if username:
     st.session_state.session_id = str(uuid.uuid4())
     API_BASE = "http://localhost:8000/login/"
     # API_BASE = "http://buildinpublic.ranaalmaaz55.repl.co/login/"
     response = requests.post(API_BASE, json={"username": username, "session_id": st.session_state.session_id})
     
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

if st.button("Signup"):
   if username:
     st.session_state.session_id = str(uuid.uuid4())
     API_BASE = "http://localhost:8000/signup/"
     # API_BASE = "http://buildinpublic.ranaalmaaz55.repl.co/signup/"
     response = requests.post(API_BASE, json={"username": username, "session_id": st.session_state.session_id})
     if response.status_code == 200:
       if response.json()["exists"]:
         st.warning("Username already exists. Please login or choose a different username.")
       else:
         st.session_state.username = username
         st.success("Signed up successfully!")
         st.switch_page("pages/frontend.py")
     else:
      st.error("Failed to connect to the server.")
   else:
     st.error("Username is required")
