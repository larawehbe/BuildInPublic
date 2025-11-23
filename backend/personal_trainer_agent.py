from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import os

# Chemin vers le fichier .env (même dossier que ce script)
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Vérifier que la clé est présente
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Veuillez définir votre clé OpenAI dans le fichier .env !")

print("Clé API détectée :", api_key is not None)  # juste pour vérifier

# Créer le client OpenAI avec la clé
client = OpenAI(api_key=api_key)

# Création de l'application FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèle pour les entrées utilisateur
class UserInput(BaseModel):
    goal: str
    experience: str
    days: int
    equipment: str

# Route pour générer le plan
@app.post("/generate_plan")
def generate_plan(data: UserInput):
    if data.days <= 0:
        return {"error": "Le nombre de jours doit être supérieur à 0"}

    prompt = f"""
    You are an expert fitness coach.
    Create a weekly workout plan:
    - Goal: {data.goal}
    - Experience: {data.experience}
    - Days/week: {data.days}
    - Equipment: {data.equipment}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert fitness coach."},
                {"role": "user", "content": prompt}
            ]
        )
        plan_text = response.choices[0].message["content"]
        return {"plan": plan_text}

    except Exception as e:
        return {"error": str(e)}
