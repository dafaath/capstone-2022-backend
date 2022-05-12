import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from uuid import uuid4


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), default=uuid4,
                primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)
    phone = Column(String, index=True, unique=True, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    photo = Column(String, default="default.png", nullable=False)
    time_created = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    time_updated = Column(
        DateTime(
            timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False)
    sessions = relationship("Session", back_populates="user")


class Session(Base):
    __tablename__ = "session"

    id = Column(UUID(as_uuid=True), default=uuid4,
                primary_key=True, index=True)
    valid = Column(Boolean, default=True, nullable=False)
    user_agent = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    user = relationship("User", back_populates="sessions")
    time_created = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    time_updated = Column(
        DateTime(
            timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False)
