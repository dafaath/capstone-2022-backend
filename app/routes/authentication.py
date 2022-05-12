from fastapi import APIRouter, Depends, Header
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from sqlalchemy.orm import Session
from app.database import get_db
from app.schema.authentication import  LoginResponse,  RefreshTokenBody, RefreshTokenResponse, RefreshTokenResponseData, RegisterBody, RegisterResponse, UserResponse
from app.schema.default_response import error_reason
from app.services.authentication import create_access_token, create_refresh_token, create_session, login_user, refresh_access_token, register_user, validate_refresh_token
from config import get_settings

router = APIRouter(prefix="/authentications",
                   tags=["Authentication"])
settings = get_settings()


@ router.post("/register", description="This path is for register new user", status_code=201, response_model=RegisterResponse, responses={409: error_reason("Email or phone is already exists in db")})
def register(body: RegisterBody, db: Session = Depends(get_db)):
    saved_user = register_user(body, db)
    response = RegisterResponse(
        status=201, message="Registration successful", data=UserResponse.from_orm(saved_user))
    return response


login_desc = f"""This path is for login after register, the login is using OAuth2 standard, you will get access token and refresh token in response. 
Access token will be only valid for {settings.jwt_access_token_expiry_minutes} minutes, after which you need to gain a new one in Refresh path, using refresh token.
"""


@ router.post("/login", description=login_desc, status_code=200, response_model=LoginResponse, responses={401: error_reason("Password or email is not correct")})
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db), user_agent: str = Header(...)):
    user = login_user(form_data, db)

    access_token = create_access_token(
        UserResponse.from_orm(user))
    session = create_session(user, user_agent, db)
    refresh_token = create_refresh_token(session, user)

    response = LoginResponse(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer", expires_in=settings.jwt_access_token_expiry_minutes*60)
    return response


@ router.post("/refresh", description=f"This path is used to refresh the access token given after login, the refresh token is only valid for {settings.jwt_access_token_expiry_minutes} minutes, after {settings.jwt_access_token_expiry_minutes} minutes you have to gain a new access token", status_code=200, response_model=RefreshTokenResponse, responses={401: error_reason("Refresh token is either expired or invalid"), 404: error_reason("When user_id or session_id in the jwt is not found in database")})
def refresh(body: RefreshTokenBody, db: Session = Depends(get_db)):
    result = validate_refresh_token(body)
    access_token = refresh_access_token(result, db)

    response = RefreshTokenResponse(
        status=200, message="Access token successfully renewed", data=RefreshTokenResponseData(access_token=access_token))
    return response
