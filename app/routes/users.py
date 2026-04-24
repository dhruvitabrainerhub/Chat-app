from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import decode_token
from app.database import get_db
from app.models import FriendRequest, User
from app.schemas import FriendRequestOut, UserOut

router = APIRouter(prefix="/users", tags=["users"])


def get_current_user(token: str, db: Session) -> User:
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=List[UserOut])
def get_users(token: str, db: Session = Depends(get_db)) -> List[User]:
    me = get_current_user(token, db)
    return db.query(User).filter(User.id != me.id).all()


@router.post("/request/{receiver_id}", response_model=FriendRequestOut)
def send_request(
    receiver_id: int, token: str, db: Session = Depends(get_db)
) -> FriendRequest:
    me = get_current_user(token, db)
    if me.id == receiver_id:
        raise HTTPException(status_code=400, detail="Cannot send request to yourself")
    existing = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.sender_id == me.id,
            FriendRequest.receiver_id == receiver_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Request already sent")
    req = FriendRequest(sender_id=me.id, receiver_id=receiver_id, status="pending")
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.get("/requests", response_model=List[FriendRequestOut])
def get_requests(token: str, db: Session = Depends(get_db)) -> List[FriendRequest]:
    me = get_current_user(token, db)
    return (
        db.query(FriendRequest)
        .filter(
            FriendRequest.receiver_id == me.id, FriendRequest.status == "pending"
        )
        .all()
    )


@router.post("/request/{request_id}/respond", response_model=FriendRequestOut)
def respond_request(
    request_id: int,
    action: str,
    token: str,
    db: Session = Depends(get_db),
) -> FriendRequest:
    me = get_current_user(token, db)
    req = db.query(FriendRequest).filter(FriendRequest.id == request_id).first()
    if not req or req.receiver_id != me.id:
        raise HTTPException(status_code=404, detail="Request not found")
    if action not in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail="Invalid action")
    req.status = action
    db.commit()
    db.refresh(req)
    return req


@router.get("/friends", response_model=List[UserOut])
def get_friends(token: str, db: Session = Depends(get_db)) -> List[User]:
    me = get_current_user(token, db)
    accepted = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.status == "accepted",
            (FriendRequest.sender_id == me.id) | (FriendRequest.receiver_id == me.id),
        )
        .all()
    )
    friend_ids = [
        r.receiver_id if r.sender_id == me.id else r.sender_id for r in accepted
    ]
    return db.query(User).filter(User.id.in_(friend_ids)).all()
