from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class FriendRequestOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    status: str
    sender: UserOut
    receiver: UserOut

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    receiver_id: int
    text: str


class MessageOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    text: str
    sender: UserOut

    model_config = {"from_attributes": True}


class WSMessage(BaseModel):
    token: str
    receiver_id: int
    text: str
