from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schema.authentication import LoginBody, Register, UserResponse
from app.models.authentication import User
from app.utils.jwt import UUIDEncoder
import bcrypt

from config import get_settings

settings = get_settings()


def register_user(user: Register, db: Session):
    email_exist = db.query(User).filter(
        User.email == user.email).first() is not None
    if email_exist:
        raise HTTPException(status_code=409, detail="Email is already exists")

    phone_exist = db.query(User).filter(
        User.phone == user.phone).first() is not None
    if phone_exist:
        raise HTTPException(
            status_code=409, detail="Phone number is already exists")

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), salt)
    db_user = User(
        email=user.email, password=hashed_password.decode('utf-8'), phone=user.phone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def login_user(payload: LoginBody, db: Session):
    user: User = db.query(User).filter(
        User.email == payload.email).first()

    if user is None:
        raise HTTPException(401, "email or password is incorrect")

    correct_password = bcrypt.checkpw(
        payload.password.encode('utf-8'), user.password.encode('utf-8'))

    if not correct_password:
        raise HTTPException(401, "email or password is incorrect")

    return user


def create_access_token(data: UserResponse, expires_delta: Optional[timedelta] = None):
    to_encode = data.dict()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    now = datetime.utcnow()

    # Mengubah id dari UUID menjadi str
    to_encode.update({"id": str(to_encode['id'])})
    to_encode.update({"exp": expire})
    to_encode.update({"iat": now})

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt
