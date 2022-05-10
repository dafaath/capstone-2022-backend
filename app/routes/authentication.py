from datetime import timedelta
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schema.authentication import LoginBody, LoginResponse, LoginResponseData, RefreshTokenBody, RefreshTokenResponse, RefreshTokenResponseData, RegisterBody, RegisterResponse, UserResponse
from app.schema.default_response import MyHTTPError, error_reason
from app.services.authentication import create_access_token, create_refresh_token, create_session, login_user, refresh_access_token, register_user, validate_refresh_token
from app.utils.jwt import decrypt_refresh_token

router = APIRouter(prefix="/authentications",
                   tags=["Authentication"])


@ router.post("/register", status_code=201, response_model=RegisterResponse)
def register(body: RegisterBody, db: Session = Depends(get_db)):
    saved_user = register_user(body, db)
    response = RegisterResponse(
        status=201, message="Registration successful", data=UserResponse.from_orm(saved_user))
    return response


@ router.post("/login", status_code=200, response_model=LoginResponse)
def login(body: LoginBody, db: Session = Depends(get_db), user_agent: str = Header(...)):
    user = login_user(body, db)

    # Create access token that will expire in 15 minutes
    access_token = create_access_token(
        UserResponse.from_orm(user))
    session = create_session(user, user_agent, db)
    refresh_token = create_refresh_token(session, user)

    response = LoginResponse(
        status=200, message="Login successful", data=LoginResponseData(access_token=access_token, refresh_token=refresh_token))
    return response


@ router.post("/refresh", description="This path is used to refresh the access token given after login, the refresh token is only valid for 15 minutes, after 15 minutes you have to gain a new access token", status_code=200, response_model=RefreshTokenResponse, responses={401: error_reason("Refresh token is either expired or invalid"), 404: error_reason("When user_id or session_id in the jwt is not found in database")})
def refresh(body: RefreshTokenBody, db: Session = Depends(get_db)):
    result = validate_refresh_token(body)
    access_token = refresh_access_token(result, db)

    response = RefreshTokenResponse(
        status=200, message="Refresh token successfully renewed", data=RefreshTokenResponseData(access_token=access_token))
    return response
