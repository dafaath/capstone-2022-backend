from datetime import datetime
from typing import Optional
from fastapi import Path
from pydantic import BaseModel, Field, EmailStr
from app.schema.default_response import ResponseTemplate
from app.schema.user import UserResponse
from app.utils.schema import AutoCamelModel, to_camel
from config import get_settings

settings = get_settings()


class LoginResponse(BaseModel):
    access_token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImYzZjYxZWQ4LTNhMDYtNDhlNi05NGE4LTkzZTU2ZDg0YjI5NiIsImVtYWlsIjoiZGFmYUBnbWFpbC5jb20iLCJwaG9uZSI6Iis2MjgxMzI5MDgyMzE0czEiLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY1MjEwMjk5MCwiaWF0IjoxNjUyMTAyMDkwfQ.SyhCaUvvvB7jMk5T7dEsGScHy6Pe5FqZhIkBEnJggT0",
        description=f"JWT access token that will expire in {settings.jwt_access_token_expiry_minutes} minutes")
    refresh_token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uX2lkIjoiOWEwYmFlZDMtMzMwMy00MjczLTkzYjYtM2NiMjUzOGI1MjdjIiwidXNlcl9pZCI6IjM3YjVlNjU4LWM3NjUtNGYyZC1hNWEwLWJjNjgwNWZjY2ZhYiIsImlhdCI6MTY1MjE2MjIyN30.EXkeCHuqA93MSTbkAoNJU06qsbQcoBRPnH6RZYEOYvo",
        description="Refresh access token, use this to refresh the access token above in /authentications/refresh path")
    token_type: str = Field(..., example="bearer")
    expires_in: int = Field(..., description="Time until access token expires (in seconds)", example=3600)
    scope: Optional[str] = Field(None, description="Authorize list of actions", example="create")


class AccessToken(UserResponse):
    id: str
    time_created: str
    time_updated: str
    iat: datetime
    exp: datetime


class RefreshToken(AutoCamelModel):
    session_id: str
    user_id: str
    iat: datetime


class RefreshTokenBody(AutoCamelModel):
    refresh_token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uX2lkIjoiOWEwYmFlZDMtMzMwMy00MjczLTkzYjYtM2NiMjUzOGI1MjdjIiwidXNlcl9pZCI6IjM3YjVlNjU4LWM3NjUtNGYyZC1hNWEwLWJjNjgwNWZjY2ZhYiIsImlhdCI6MTY1MjE2MjIyN30.EXkeCHuqA93MSTbkAoNJU06qsbQcoBRPnH6RZYEOYvo",
        description="Refresh token gained from response after login")


class RefreshTokenResponseData(AutoCamelModel):
    access_token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImYzZjYxZWQ4LTNhMDYtNDhlNi05NGE4LTkzZTU2ZDg0YjI5NiIsImVtYWlsIjoiZGFmYUBnbWFpbC5jb20iLCJwaG9uZSI6Iis2MjgxMzI5MDgyMzE0czEiLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY1MjEwMjk5MCwiaWF0IjoxNjUyMTAyMDkwfQ.SyhCaUvvvB7jMk5T7dEsGScHy6Pe5FqZhIkBEnJggT0",
        description=f"JWT access token that will expire in {settings.jwt_access_token_expiry_minutes} minutes")


class RefreshTokenResponse(ResponseTemplate):
    data: RefreshTokenResponseData


class LoginGoogleBody(AutoCamelModel):
    token: str = Path(..., description="Google jwt token after sign in with google")


class GoogleJWTPayload(AutoCamelModel):
    iss: str
    nbf: int
    aud: str
    sub: str
    email: str
    email_verified: bool
    azp: str
    name: str
    picture: str
    given_name: str
    family_name: str
    iat: int
    exp: int
    jti: str
