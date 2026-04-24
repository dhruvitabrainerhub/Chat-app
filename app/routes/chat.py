from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.auth import decode_token
from app.database import get_db, SessionLocal
from app.models import FriendRequest, Message, User
from app.schemas import MessageOut

router = APIRouter(prefix="/chat", tags=["chat"])

# {user_id: websocket}
active_connections: Dict[int, WebSocket] = {}


def are_friends(db: Session, user1_id: int, user2_id: int) -> bool:
    return (
        db.query(FriendRequest)
        .filter(
            FriendRequest.status == "accepted",
            (
                (FriendRequest.sender_id == user1_id)
                & (FriendRequest.receiver_id == user2_id)
            )
            | (
                (FriendRequest.sender_id == user2_id)
                & (FriendRequest.receiver_id == user1_id)
            ),
        )
        .first()
        is not None
    )


@router.get("/history/{friend_id}", response_model=List[MessageOut])
def get_history(
    friend_id: int, token: str, db: Session = Depends(get_db)
) -> List[Message]:
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    me = int(user_id)
    if not are_friends(db, me, friend_id):
        raise HTTPException(status_code=403, detail="Not friends")
    return (
        db.query(Message)
        .filter(
            ((Message.sender_id == me) & (Message.receiver_id == friend_id))
            | ((Message.sender_id == friend_id) & (Message.receiver_id == me))
        )
        .order_by(Message.created_at)
        .all()
    )


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    db = SessionLocal()
    user_id = None
    try:
        while True:
            data = await websocket.receive_json()
            token = data.get("token")
            receiver_id = data.get("receiver_id")
            text = data.get("text", "").strip()

            uid = decode_token(token)
            if not uid:
                await websocket.send_json({"error": "Invalid token"})
                continue

            user_id = int(uid)
            active_connections[user_id] = websocket

            if not text or not receiver_id:
                continue

            if not are_friends(db, user_id, receiver_id):
                await websocket.send_json({"error": "Not friends"})
                continue

            msg = Message(sender_id=user_id, receiver_id=receiver_id, text=text)
            db.add(msg)
            db.commit()
            db.refresh(msg)

            sender = db.query(User).filter(User.id == user_id).first()
            payload = {
                "id": msg.id,
                "sender_id": user_id,
                "sender_username": sender.username if sender else "",
                "receiver_id": receiver_id,
                "text": text,
            }

            await websocket.send_json(payload)
            if receiver_id in active_connections:
                await active_connections[receiver_id].send_json(payload)

    except WebSocketDisconnect:
        if user_id and user_id in active_connections:
            del active_connections[user_id]
    finally:
        db.close()
