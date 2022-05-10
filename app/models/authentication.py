from email.policy import default
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from uuid import uuid4


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), default=uuid4,
                primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone = Column(String, index=True, unique=True)
    is_active = Column(Boolean, default=True)
    time_created = Column(DateTime(timezone=True), default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    sessions = relationship("Session", back_populates="user")


class Session(Base):
    __tablename__ = "session"

    id = Column(UUID(as_uuid=True), default=uuid4,
                primary_key=True, index=True)
    valid = Column(Boolean, default=True)
    user_agent = Column(String)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    user = relationship("User", back_populates="sessions")
    time_created = Column(DateTime(timezone=True), default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
