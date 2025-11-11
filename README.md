# 💪 AI Personal Trainer Agent

This mini-project is part of the **“Create Your Own Internship”** challenge by **Lara Wehbe**.

You’ll build a simple **AI-powered Personal Trainer** that asks the right questions, collects your answers, and generates a personalized **gym plan** using OpenAI’s API.

---## 🧩 Project Overview

**Step 1:** `api.py` → the backend (**FastAPI**)

- Receives user data (goal, experience, days, equipment)
- Generates a customized gym plan using an AI model

**Step 2:** `frontend.py` → the frontend (**Streamlit**)

- Interactive form where users answer questions
- Sends data to the FastAPI endpoint and displays the plan

---
## ⚙️ Setup Instructions

1. **Create and activate a virtual environment**
    
    ### 🪟 On Windows:
    
    ```bash
    python -m venv venv
    venv\Scripts\activate
    
    ```
    
    ### 🐧 On macOS / Linux:
    
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    
    ```
    

---

2. **Install dependencies**
    
    ```bash
    pip install fastapi uvicorn openai streamlit requests python-dotenv
    
    ```
    

---

3. **Set up your environment variables**
    - In your project folder, you’ll find a file called `.sample.env`
    - Duplicate it and rename the copy to `.env`
    
    Then open the `.env` file and add your OpenAI API key:
    
    ```
    OPENAI_API_KEY=sk-your-api-key-here
    
    ```
    
    ⚠️ Never share your API key publicly or commit it to GitHub.
    

---

4. **Run the backend**
    
    ```bash
    uvicorn personal_trainer_agent:app --reload
    
    ```
    

---

6. **Run the frontend**
    
    ```bash
    streamlit run step2_streamlit_app.py
    
    ```
    

---

7. **Open the Streamlit app**
    - Go to http://localhost:8501
    - Fill in your details → get your personalized gym plan 🏋️
---

---

## 🧠 Learning Goals

You’ll practice how to:

- Design structured prompts for AI models
- Connect a frontend (Streamlit) to a backend (FastAPI)
- Use APIs to generate personalized content
- Think like an **AI product builder**, not just a coder

---

## 🚀 Tasks to Extend the Project

### To-Do Tasks

| Step | Focus Area | What to Learn | To-Do Tasks | Difficulty |
| --- | --- | --- | --- | --- |
| 🧩 **Step 2** | **Backend Foundations** | Learn **FastAPI** basics (routes, POST requests, models). | Build a `/generate_plan` endpoint that receives user data and returns a plan. | 🟢 Easy |
|  | **Database Integration** | Learn **SQLite3** for local storage and **SQLAlchemy ORM** to connect databases inside Python. | Add a simple table to store user inputs and generated plans. | 🟡 Medium |
|  | **Frontend Frameworks** | Learn **Streamlit** or **Gradio** for interactive UIs. | Create a clean UI form to send user data to the backend and display the plan. | 🟢 Easy |
|  | **Model Integration** | Learn how to call **OpenAI API** or **Hugging Face Transformers** inside Python. | Replace static responses with dynamic AI-generated plans. | 🟡 Medium |
|  | **AI Agent Design** | Learn **LangChain** basics and **Agent design patterns** (tool-calling, memory, context). | Convert your simple plan generator into a *chatbot agent* that asks follow-up questions dynamically. | 🔴 Advanced |

---

| Step | Focus Area | What to Learn | To-Do Tasks | Difficulty |
| --- | --- | --- | --- | --- |
| 🚀 **Step 3** | **Deployment Basics** | Learn **Docker** fundamentals (images, containers, Dockerfile). | Dockerize both your FastAPI backend and Streamlit frontend. | 🟡 Medium |
|  | **Cloud Deployment** | Learn to deploy AI apps on **DigitalOcean** (Droplets / App Platform). | Deploy your app publicly so users can access it. *(Note: not free)* | 🔴 Advanced |
|  | **Testing & Optimization** | Test endpoints and UI; learn about logs and debugging on cloud. | Verify both the backend API and frontend app work correctly online. | 🟡 Medium |
|  | **Public Sharing** | Learn how to document and present your work online. | Share your deployed link, GitHub repo, and story on LinkedIn or Twitter. | 🟢 Easy |

---

## 🌟 Feature Expansion Ideas

| # | New Feature | Goal | Skills Practiced | Difficulty |
| --- | --- | --- | --- | --- |
| 1 | 📸 **Food Image Upload** | Let users upload a photo of their meal. | Learn **image upload handling** and **vision APIs**(e.g. Gemini, OpenAI, or Hugging Face). | 🔴 Advanced |
| 2 | 🔢 **Calorie Estimator** | Automatically estimate calories from a meal image. | Learn **multimodal AI** and integrate a **vision model**. | 🔴 Advanced |
| 3 | 📅 **Weekly Progress Tracker** | Track and visualize weekly training data. | Learn **database relationships** and **data visualization** (Matplotlib / Plotly). | 🟡 Medium |
| 4 | 🧠 **Smart Suggestions** | AI analyzes your progress and adjusts your next-week plan. | Learn **prompt chaining** and **LangChain memory**. | 🔴 Advanced |
| 5 | 🧩 **Customizable Agent Personas** | Create different trainer styles (strict coach, friendly motivator, etc.). | Learn **prompt engineering** and **persona conditioning**. | 🟡 Medium |

---

## 🧧 Bonus Idea

Turn this into a **portfolio project** 💼

- Rename the app → *FitAI Coach*, *SmartTrainer*, or your brand name
- Add your own logo & color palette
- Post on LinkedIn:
    
    > “Instead of waiting for an internship, I built my own using AI.”
    > 

---

## 🪜 Next Step: Build in Public

You’ve learned how to:

- Create your own internship
- Build an AI-powered app
- Deploy it and share it with the world

Now it’s your turn to take it further 👇

1. **Fork this repository**
    
    → Make your own copy and start customizing it.
    
2. **Add your advanced project**
    
    → Improve the AI agent, add new features, or design your own domain-specific version.
    
3. **Do a Pull Request**
    
    → Create a pull request (PR) on this repository, and share it. If all is well, I will accept it, and we will build it together (Everyone of you is more than welcome to try it out!)
    
    → Share your version back here — let others see how you built your own internship.
    
4. **Build in Public**
    
    → Post your progress on LinkedIn, tag **@larawehbe_**, and use the hashtag **#AICareerAccelerator**
    
    → Inspire the next wave of AI engineers 🚀
    

## Links and tutorials:

FastAPI: https://fastapi.tiangolo.com/

Huggingface: https://huggingface.co/

Streamlit: https://streamlit.io/

SQLite3 or PSQL: Choose anyone of them and find a good tutorial on youtube on it

SQLAlchemy: https://docs.sqlalchemy.org/en/20/dialects/sqlite.html

LangChain: https://www.langchain.com/

Docker: https://www.docker.com/

Digital Ocean (Cloud Provider): https://www.digitalocean.com/