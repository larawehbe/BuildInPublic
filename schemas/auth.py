from pydantic import BaseModel


class AuthInput(BaseModel):
    username: str
    session_id: str
