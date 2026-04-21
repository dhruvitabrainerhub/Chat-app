from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException

from app.models import Message, MessageCreate, Room

router = APIRouter()

messages: List[Message] = []
rooms: List[Room] = [
    Room(name="general", description="General chat"),
    Room(name="random", description="Random topics"),
    Room(name="tech", description="Tech discussions"),
]
counter: int = 0


@router.get("/rooms", response_model=List[Room])
def get_rooms() -> List[Room]:
    return rooms


@router.get("/messages", response_model=List[Message])
def get_messages(room: str = "general") -> List[Message]:
    return [m for m in messages if m.room == room]


@router.post("/messages", response_model=Message)
def send_message(payload: MessageCreate) -> Message:
    global counter
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    counter += 1
    msg = Message(
        id=counter,
        username=payload.username,
        room=payload.room,
        text=payload.text,
        timestamp=datetime.now().strftime("%H:%M"),
    )
    messages.append(msg)
    return msg


@router.delete("/messages", status_code=204)
def clear_messages(room: str = "general") -> None:
    global messages
    messages = [m for m in messages if m.room != room]
