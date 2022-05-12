from sqlalchemy.orm import Session
from typing import Optional

from app.models.authentication import User


def get_user_by_email(email: str, db: Session):
    user: Optional[User] = db.query(User).filter(
        User.email == email).first()
    return user
