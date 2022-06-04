from datetime import datetime, timedelta
from typing import Union

import bcrypt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from google.auth.transport import requests
from google.oauth2 import id_token
from jose import jwt
from sqlalchemy.orm import Session

from app.models import Session as UserSession
from app.models import User
from app.schema.authentication import (AccessToken, GoogleJWTPayload,
                                       RefreshToken, RefreshTokenBody,
                                       UserResponse)
from app.services.user import get_user_by_email
from app.utils.jwt import (AccessTokenDecrypt, RefreshTokenDecrypt,
                           decrypt_access_token, decrypt_refresh_token)
from config import get_settings

settings = get_settings()


def login_user(payload: OAuth2PasswordRequestForm, db: Session):
    user: User = get_user_by_email(payload.username, db)
    if user is None:
        raise HTTPException(401, "email or password is incorrect")

    correct_password = bcrypt.checkpw(
        payload.password.encode('utf-8'), user.password.encode('utf-8'))

    if not correct_password:
        raise HTTPException(401, "email or password is incorrect")

    return user


def create_access_token(data: UserResponse, expire_delta: timedelta = None):
    if expire_delta is None:
        expire_delta = timedelta(minutes=settings.jwt_access_token_expiry_minutes)
    expire = datetime.utcnow() + expire_delta
    now = datetime.utcnow()

    # Mengubah id dari UUID menjadi str
    data.id = str(data.id)
    data.time_created = data.time_created.isoformat()
    data.time_updated = data.time_updated.isoformat()
    payload: AccessToken = AccessToken(**data.dict(), exp=expire, iat=now)
    payload_dict = payload.dict()

    access_token = jwt.encode(
        payload_dict, settings.jwt_access_token_secret_key, algorithm=settings.jwt_algorithm)
    return access_token


def create_refresh_token(session: UserSession, user: User):
    now = datetime.utcnow()
    payload: RefreshToken = RefreshToken(
        session_id=str(session.id), user_id=str(user.id), iat=now)
    payload_dict = payload.dict()

    refresh_token = jwt.encode(
        payload_dict, settings.jwt_refresh_token_secret_key, algorithm=settings.jwt_algorithm)
    return refresh_token


def check_jwt_result(result: Union[RefreshTokenDecrypt, AccessTokenDecrypt]):
    token_type = ""
    if(isinstance(result, RefreshTokenDecrypt)):
        token_type = "Refresh"
    else:
        token_type = "Access"

    if result.expired:
        raise HTTPException(
            401, detail=f"{token_type} token is not already expired")
    if not result.valid:
        raise HTTPException(401, detail=f"{token_type} token is not valid")


def validate_access_token(access_token: RefreshTokenBody):
    result = decrypt_access_token(access_token)
    check_jwt_result(result)
    return result


def validate_refresh_token(refresh_token: RefreshTokenBody):
    result = decrypt_refresh_token(refresh_token)
    check_jwt_result(result)
    return result


def refresh_access_token(result: RefreshTokenDecrypt, db: Session):
    user: User = db.query(User).filter(
        User.id == result.payload.user_id).first()
    session: UserSession = db.query(UserSession).filter(
        UserSession.id == result.payload.session_id).first()

    if user is None:
        raise HTTPException(404, "The user id in the jwt does not exists")

    if session is None:
        raise HTTPException(404, "The session id in the jwt does not exists")

    access_token = create_access_token(
        UserResponse.from_orm(user))
    return access_token


def create_session(user: User, user_agent: str, db: Session):
    session = UserSession(user_agent=user_agent, user=user)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_current_user(token: str, db: Session):
    expired_exception = HTTPException(
        status_code=401,
        detail="This access token is expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    not_valid_exception = HTTPException(
        status_code=401,
        detail="This access token is not valid",
        headers={"WWW-Authenticate": "Bearer"},
    )
    result = decrypt_access_token(token)

    if result.expired:
        raise expired_exception

    if not result.valid:
        raise not_valid_exception

    user: User = db.query(User).filter(
        User.id == result.payload.id).first()
    if user is None:
        raise expired_exception

    return user


def validate_google_csrf_token(csrf_token_body: str, csrf_token_cookie: str):
    if not csrf_token_cookie:
        HTTPException(401, 'No CSRF token in Cookie.')
    if not csrf_token_body:
        HTTPException(401, 'No CSRF token in post body.')
    if csrf_token_cookie != csrf_token_body:
        HTTPException(401, 'Failed to verify double submit cookie.')


def validate_google_token(token: str):
    try:
        payload = id_token.verify_oauth2_token(token, requests.Request(), settings.google_client_id)
        payload = GoogleJWTPayload(**payload)
        return payload
    except ValueError:
        # Invalid token
        raise HTTPException(401, "The google token is invalid")


def register_google_user(email: str, fullname: str, db: Session):
    db_user = User(
        email=email, fullname=fullname)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
