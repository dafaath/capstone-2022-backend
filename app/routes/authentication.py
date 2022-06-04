from datetime import timedelta

from fastapi import APIRouter, Depends, Form, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schema.authentication import (LoginResponse, RefreshTokenBody,
                                       RefreshTokenResponse,
                                       RefreshTokenResponseData, UserResponse)
from app.schema.default_response import error_reason
from app.services.authentication import (create_access_token,
                                         create_refresh_token, create_session,
                                         login_user, refresh_access_token,
                                         register_google_user,
                                         validate_google_token,
                                         validate_refresh_token)
from app.services.user import get_user_by_email
from config import get_settings

router = APIRouter(prefix="/authentications",
                   tags=["Authentication"])
settings = get_settings()


login_desc = f"""This path is for login after register, the login is using OAuth2 standard, you will get access token and refresh token in response.
Access token will be only valid for {settings.jwt_access_token_expiry_minutes} minutes, after which you need to gain a new one in Refresh path, using refresh token.
"""


@ router.post("/login", description=login_desc, status_code=200, response_model=LoginResponse,
              responses={401: error_reason("Password or email is not correct")})
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db),
          user_agent: str = Header(...,
                                   example="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
                                   description="The sender user agent"),
          ):
    user = login_user(form_data, db)

    access_token = create_access_token(
        UserResponse.from_orm(user))
    session = create_session(user, user_agent, db)
    refresh_token = create_refresh_token(session, user)

    data = LoginResponse(
        message="Successfully login",
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expiry_minutes * 60,
        **UserResponse.from_orm(user).dict())
    return data


@ router.post("/login-test",
              description="TEST Version of login, access token only last 10 seconds",
              status_code=200,
              response_model=LoginResponse,
              responses={401: error_reason("Password or email is not correct")})
def login_test(form_data: OAuth2PasswordRequestForm = Depends(),
               db: Session = Depends(get_db),
               user_agent: str = Header(...,
                                        example="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
                                        description="The sender user agent"),
               ):
    user = login_user(form_data, db)

    access_token = create_access_token(
        UserResponse.from_orm(user), expire_delta=timedelta(seconds=10))
    session = create_session(user, user_agent, db)
    refresh_token = create_refresh_token(session, user)

    data = LoginResponse(
        message="Successfully login test",
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=10,
        **UserResponse.from_orm(user).dict())
    return data


login_google_desc = f"""This path is for sending google JWT after login with google, you will get access token and refresh token in response.
Access token will be only valid for {settings.jwt_access_token_expiry_minutes} minutes, after which you need to gain a new one in Refresh path, using refresh token.
"""


@ router.post("/login/google", description=login_google_desc, status_code=200,
              response_model=LoginResponse, responses={401: error_reason("The google token is invalid")})
async def login_google(
    credential: str = Form(..., description="The google token that you got after login with google"),
    db: Session = Depends(get_db),
    user_agent: str = Header(..., example="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36", description="The sender user agent"),
):
    payload = validate_google_token(credential)
    user = get_user_by_email(payload.email, db)
    if user is None:
        # User not registered in database
        user = register_google_user(payload.email, payload.name, db)

    access_token = create_access_token(
        UserResponse.from_orm(user))
    session = create_session(user, user_agent, db)
    refresh_token = create_refresh_token(session, user)

    data = LoginResponse(
        message="Successfully login",
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expiry_minutes * 60,
        **UserResponse.from_orm(user).dict())
    return data


@ router.post(
    "/refresh",
    description=f"This path is used to refresh the access token given after login, the refresh token is only valid for {settings.jwt_access_token_expiry_minutes} minutes, after {settings.jwt_access_token_expiry_minutes} minutes you have to gain a new access token",
    status_code=200,
    response_model=RefreshTokenResponse,
    responses={
        401: error_reason("Refresh token is either expired or invalid"),
        404: error_reason("When user_id or session_id in the jwt is not found in database")})
def refresh(body: RefreshTokenBody, db: Session = Depends(get_db)):
    result = validate_refresh_token(body.refresh_token)
    access_token = refresh_access_token(result, db)

    response = RefreshTokenResponse(

        message="Access token successfully renewed",
        data=RefreshTokenResponseData(
            access_token=access_token))
    return response
