from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from groq import Groq
import dbSQLAlchemy as db
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableSequence
from pydantic import SecretStr
import json

load_dotenv()
key = os.getenv("GROQ_API")
if not key:
    raise ValueError("Groq API key not found in environment variables.")
client = Groq(api_key=key)
llm = ChatGroq(temperature=0.7, model="llama-3.1-8b-instant", api_key=SecretStr(key))

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
        (
                "system",
                """You are an AI personal trainer.

    User preferences:
    - Goal: {goal}
    - Experience: {experience}
    - Days per week: {days_per_week}
    - Equipment: {equipment}
    - Coaching tone: {tone}

    Adapt all responses to these preferences."""
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])



class UserInput(BaseModel):
    username: str
    age: int
    gender: str
    goal: str
    experience: str
    days_per_week: int
    equipment: str
    tone: str
    weight: int
    height: int

class ChatInput(BaseModel):
    username: str
    message: str

class AuthInput(BaseModel):
    username: str
    session_id: str


app = FastAPI()


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
        "age": data.age,
        "gender": data.gender,
        "goal": data.goal,
        "experience": data.experience,
        "days_per_week": data.days_per_week,
        "equipment": data.equipment,
        "tone": data.tone,
        "weight": data.weight,
        "height": data.height
    }
    if not db.get_user_preferences(db.session, data.username):
        db.create_user_preferences(db.session, data.username, json.dumps(preferences_json))
    else:
        db.update_user_preferences(db.session, data.username, json.dumps(preferences_json))

@app.get("/chat_history/{username}")
def get_chat_history(username: str):
    messages = db.get_chat_messages(db.session, username)
    return {"messages": [
        {"role": msg.role, "content": msg.content} for msg in messages
    ]
           }


@app.post("/chat/")
def chat(data: ChatInput):
    print("connected to fastapi")
    # 1. Load user preferences
    user_preferences = db.get_user_preferences(db.session, data.username)
    messages = db.get_chat_messages(db.session, data.username)
    # 2. Build memory
    print("got preferences and history")
    memory = build_memory([
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ])
    print("memory built")

    # 3. Build prompt template
    prompt = build_prompt_template()
    print("prompt built")
    # 4. Combine prompt and LLM into a RunnableSequence
    chain = RunnableSequence(prompt, llm)
    print("chain built")
    if not user_preferences:
        return {"response": "Please set your preferences first."}

    preferences = json.loads(str(user_preferences.preferences_json))
    print("Memory:", memory)
    # 5. Invoke chain with context
    response = chain.invoke({
        "goal":
        preferences["goal"],
        "experience":
        preferences["experience"],
        "days_per_week":
        preferences["days_per_week"],
        "equipment":
        preferences["equipment"],
        "tone":
        preferences["tone"],
        "chat_history": memory,
        "input": data.message
    })

    assistant_reply = str(response.content)

    # 6. Save messages to DB
    db.create_chat_message(db.session, data.username, "user", data.message)
    db.create_chat_message(db.session, data.username, "assistant", assistant_reply)
    

    return {"response": assistant_reply}

    
    


