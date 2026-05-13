from pydantic import BaseModel


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
