from pydantic import BaseModel


class ChatInput(BaseModel):
    username: str
    message: str
