from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schema.authentication import AccessToken, GoogleJWTPayload, RefreshToken, RefreshTokenBody, RegisterBody, UserResponse
from app.models.authentication import User, Session as UserSession
import bcrypt
from app.services.user import get_user_by_email
from app.utils.jwt import RefreshTokenDecrypt, decrypt_access_token, decrypt_refresh_token
from google.oauth2 import id_token
from google.auth.transport import requests

from config import get_settings

settings = get_settings()


def register_user(user: RegisterBody, db: Session):
    email_exist = get_user_by_email(user.email, db) is not None
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


def login_user(payload: OAuth2PasswordRequestForm, db: Session):
    user: User = get_user_by_email(payload.username, db)
    if user is None:
        raise HTTPException(401, "email or password is incorrect")

    correct_password = bcrypt.checkpw(
        payload.password.encode('utf-8'), user.password.encode('utf-8'))

    if not correct_password:
        raise HTTPException(401, "email or password is incorrect")

    return user


def create_access_token(data: UserResponse):
    expires_delta = timedelta(minutes=settings.jwt_access_token_expiry_minutes)
    expire = datetime.utcnow() + expires_delta
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


def validate_refresh_token(body: RefreshTokenBody):
    result = decrypt_refresh_token(body.refresh_token)
    if result.expired:
        raise HTTPException(
            401, detail="Refresh token is not already expired")
    if not result.valid:
        raise HTTPException(401, detail="Refresh token is not valid")
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


def register_google_user(email: str, db: Session):
    db_user = User(
        email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
