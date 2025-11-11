import openai
from dotenv import load_dotenv
import os
load_dotenv()

client = openai.OpenAI()

openai.api_key = "YOUR_OPENAI_API_KEY"
def main(): 
    print("💪 Welcome to your AI Personal Trainer!")
    goal = input("What's your fitness goal? ")
    experience = input("What's your experience level (beginner/intermediate/advanced)? ")
    days = input("How many days per week can you train? ")
    equipment = input("What equipment do you have? ")

    prompt = f"""
    You are a personal trainer. Create a 1-week gym plan for someone with:
    Goal: {goal}
    Experience: {experience}
    Days per week: {days}
    Equipment: {equipment}
    Return it as a structured text plan (Day 1, Day 2...).
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    print("\n🏋️ Your Gym Plan:\n")
    print(response.choices[0].message.content)


