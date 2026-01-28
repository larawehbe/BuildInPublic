from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from groq import Groq
import dbSQLAlchemy as db
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableSequence


load_dotenv()
key = os.getenv("GroqAPI")
client = Groq(api_key=key)
llm = ChatGroq(temperature=0.7, model="llama3-8b-8192", api_key=key)

# Build LangChain memory
def build_memory(messages: list):
    history = [
        HumanMessage(content=m["content"]) if m["role"] == "user"
        else AIMessage(content=m["content"])
        for m in messages
    ]

    return history


# Build prompt template

def build_prompt_template():
    return ChatPromptTemplate.from_messages([
        ("system",
        """You are an AI personal trainer.

    User preferences:
    - Goal: {goal}
    - Experience: {experience}
    - Days per week: {days_per_week}
    - Equipment: {equipment}
    - Coaching tone: {tone}

    Adapt all responses to these preferences."""
            ),
            ("ai", "{chat_history}"),
            ("human", "{input}")
        ])


class UserInput(BaseModel):
    username: str
    goal: str
    experience: str
    days_per_week: int
    equipment: str
    tone: str

class ChatInput(BaseModel):
    username: str
    message: str
    messages: list

class AuthInput(BaseModel):
    username: str
    session_id: str


app = FastAPI()


# @app.post("/generate_plan/")
# def generate_plan(data: UserInput):
#     prompt = f"""
#     You are an expert fitness coach.
#     Create a weekly workout plan:
#     - Goal: {data.goal}
#     - Experience: {data.experience}
#     - Days/week: {data.days_per_week}
#     - Equipment: {data.equipment}
#     """
#     try:
#         response = client.chat.completions.create(
#             model="llama3-8b-8192",
#             messages=[{
#                 "role": "system",
#                 "content": "You are an expert fitness coach."
#             }, {
#                 "role": "user",
#                 "content": prompt
#             }])
#         plan_text = response.choices[0].message.content
#         return {"gym_plan": plan_text}

#     except Exception as e:
#         return {"error": str(e)}

@app.post("/login/")
def login(data: AuthInput):
    if data.username:
        user = db.get_user(db.session, data.username)
        if user:
            db.update_session(db.session, data.username, data.session_id)
            return {"exists": True}
        else:
            return {"exists": False}

@app.post("/signup/")
def signup(data: AuthInput):
    if data.username:
        user = db.get_user(db.session, data.username)
        if user:
            return {"exists": True}
        else:
            db.create_user(db.session, data.username, data.session_id)
            return {"exists": False}

@app.post("/update_preferences/")
def update_preferences(data: UserInput):
    preferences_json = {
        "goal": data.goal,
        "experience": data.experience,
        "days_per_week": data.days_per_week,
        "equipment": data.equipment,
        "tone": data.tone
    }
    db.update_user_preferences(db.session, data.username, str(preferences_json))

@app.get("/chat_history/{username}")
def get_chat_history(username: str):
    messages = db.get_chat_messages(db.session, username)
    return {"messages": messages}


@app.post("/chat/")
def chat(data: ChatInput):
    # 1. Load user preferences
    user_preferences = db.get_user_preferences(db.session, data.username)

    # 2. Build memory
    memory = build_memory(data.messages)

    # 3. Build prompt template
    prompt = build_prompt_template()

    # 4. Combine prompt and LLM into a RunnableSequence
    chain = RunnableSequence([prompt, llm])

    # 5. Invoke chain with context
    response = chain.invoke({
        "goal": user_preferences.preferences_json["goal"],
        "experience": user_preferences.preferences_json["experience"],
        "days_per_week": user_preferences.preferences_json["days_per_week"],
        "equipment": user_preferences.preferences_json["equipment"],
        "tone": user_preferences.preferences_json["tone"],
        "chat_history": memory.messages,  # <-- new way to access messages
        "input": data.message
    })

    assistant_reply = response.content

    # 6. Save messages to DB
    db.create_chat_message(db.session, data.username, "user", data.message)
    db.create_chat_message(db.session, data.username, "assistant", assistant_reply)
    

    return {"response": assistant_reply}

    
    


