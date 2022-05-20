from typing import Optional

import bcrypt
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.schema.user import RegisterBody, UpdateUserBody


def register_user(user: RegisterBody, db: Session, role: UserRole = UserRole.REGULAR):
    email_exist = get_user_by_email(user.email, db) is not None
    if email_exist:
        raise HTTPException(status_code=409, detail="Email is already exists")

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), salt)
    db_user = User(
        email=user.email, password=hashed_password.decode('utf-8'), fullname=user.fullname, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_user(db: Session):
    users: list[User] = db.query(User).all()
    return users


def get_user_by_id(user_id: str, db: Session):
    user: Optional[User] = db.query(User).filter(
        User.id == user_id).first()
    return user


def get_user_by_id_or_error(user_id: str, db: Session):
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(404, f"There is no user with id {user_id}")
    return user


def get_user_by_email(email: str, db: Session):
    user: Optional[User] = db.query(User).filter(
        User.email == email).first()
    return user


def get_user_by_email_or_error(email: str, db: Session):
    user = get_user_by_email(email, db)
    if not user:
        raise HTTPException(404, f"There is no user with email {email}")
    return user


def update_user(user: User, body: UpdateUserBody, db: Session):
    data = body.dict(exclude_none=True, exclude={"current_password", "new_password"})
    # Jika ingin update password
    if body.current_password and body.new_password:
        # Is current password same as db
        correct_password = bcrypt.checkpw(
            body.current_password.encode('utf-8'), user.password.encode('utf-8'))
        if correct_password:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(body.new_password.encode('utf-8'), salt)
            data["password"] = hashed_password.decode('utf-8')
        else:
            raise HTTPException(403, "Current password is incorrect")

    for key, value in data.items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(user: User, db: Session):
    db.delete(user)
    db.commit()
    return user
