from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Message(BaseModel):
    id: int
    username: str
    room: str
    text: str
    timestamp: str


class MessageCreate(BaseModel):
    username: str
    room: str
    text: str


class Room(BaseModel):
    name: str
    description: Optional[str] = None
