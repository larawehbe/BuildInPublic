from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os

AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
AI_INTEGRATIONS_OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")

client = OpenAI(
    api_key=AI_INTEGRATIONS_OPENAI_API_KEY,
    base_url=AI_INTEGRATIONS_OPENAI_BASE_URL
)

app = FastAPI()

class UserInfo(BaseModel):
    goal: str
    experience: str
    days_per_week: int
    equipment: str

@app.post("/generate_plan/")
async def generate_plan(user: UserInfo):
    prompt = f"""
    You are a personal fitness trainer.
    Create a 1-week gym plan for someone with:
    - Goal: {user.goal}
    - Experience level: {user.experience}
    - Days per week available: {user.days_per_week}
    - Available equipment: {user.equipment}

    Return the plan as a simple, structured list (Day 1, Day 2, ...).
    """

    # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
    # do not change this unless explicitly requested by the user
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    plan = response.choices[0].message.content
    return {"gym_plan": plan}
