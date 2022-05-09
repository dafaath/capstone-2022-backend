from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base
from uuid import uuid4


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), default=uuid4(),
                primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    telephone = Column(String, index=True)
    is_active = Column(Boolean, default=True)
