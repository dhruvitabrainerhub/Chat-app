from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    sent_requests = relationship(
        "FriendRequest", foreign_keys="FriendRequest.sender_id", back_populates="sender"
    )
    received_requests = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.receiver_id",
        back_populates="receiver",
    )


class FriendRequest(Base):
    __tablename__ = "friend_requests"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(
        Enum("pending", "accepted", "rejected", name="request_status"),
        default="pending",
    )
    created_at = Column(DateTime, default=func.now())

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_requests")
    receiver = relationship(
        "User", foreign_keys=[receiver_id], back_populates="received_requests"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
