import datetime
import enum
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.database import Base
from config import get_settings

settings = get_settings()


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    REGULAR = "REGULAR"


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), default=uuid4,
                primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)
    phone = Column(String, index=True, unique=True, nullable=True)
    fullname = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    _photo = Column(String, default="default.png", nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.REGULAR)
    time_created = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    time_updated = Column(
        DateTime(
            timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False)
    sessions = relationship("Session", back_populates="user", cascade="all, delete")

    @hybrid_property
    def photo(self):
        if "https" in self._photo or "http" in self._photo:
            return self._photo

        return settings.static_file_routes + self._photo

    @photo.setter
    def photo(self, value):
        self._photo = value


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
