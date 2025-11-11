# personal_trainer_agent.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
import openai
from dotenv import load_dotenv
import os
load_dotenv()
client = openai.OpenAI()

# Initialize FastAPI app
app = FastAPI()

# ✅ Replace with your actual API key

# Define data structure for user inputs
class UserInfo(BaseModel):
    goal: str
    experience: str
    days_per_week: int
    equipment: str

@app.post("/generate_plan/")
async def generate_plan(user: UserInfo):
    """
    Basic AI Agent:
    - Takes user's fitness info
    - Generates a simple gym plan
    """
    prompt = f"""
    You are a personal fitness trainer.
    Create a 1-week gym plan for someone with:
    - Goal: {user.goal}
    - Experience level: {user.experience}
    - Days per week available: {user.days_per_week}
    - Available equipment: {user.equipment}

    Return the plan as a simple, structured list (Day 1, Day 2, ...).
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    plan = response.choices[0].message.content
    return {"gym_plan": plan}
