from datetime import date, datetime
from doctest import Example
from typing import Optional
from uuid import UUID
from fastapi import Path
from pydantic import BaseModel, Field, EmailStr
from app.models.authentication import User
from app.schema.default_response import ResponseTemplate
from app.utils.schema import AutoCamelModel
from config import get_settings

settings = get_settings()

class RegisterBase(AutoCamelModel):
    email: EmailStr = Field(..., example="example@gmail.com",
                            description="User email")
    phone: str = Field(..., example="+6281390823143",
                       regex=r"\+[\d]{8,15}",
                       description="User telephone number with country code in front, with a 8-15 character length")


class RegisterBody(RegisterBase):
    password: str = Field(..., description="User password")


class UserResponse(RegisterBase):
    id: UUID = Field(..., description="User id in UUID format")
    is_active: bool = Field(
        ..., description="Is user is an active user or not")


class RegisterResponse(ResponseTemplate):
    data: UserResponse


class LoginResponse(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImYzZjYxZWQ4LTNhMDYtNDhlNi05NGE4LTkzZTU2ZDg0YjI5NiIsImVtYWlsIjoiZGFmYUBnbWFpbC5jb20iLCJwaG9uZSI6Iis2MjgxMzI5MDgyMzE0czEiLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY1MjEwMjk5MCwiaWF0IjoxNjUyMTAyMDkwfQ.SyhCaUvvvB7jMk5T7dEsGScHy6Pe5FqZhIkBEnJggT0", description=f"JWT access token that will expire in {settings.jwt_access_token_expiry_minutes} minutes")
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uX2lkIjoiOWEwYmFlZDMtMzMwMy00MjczLTkzYjYtM2NiMjUzOGI1MjdjIiwidXNlcl9pZCI6IjM3YjVlNjU4LWM3NjUtNGYyZC1hNWEwLWJjNjgwNWZjY2ZhYiIsImlhdCI6MTY1MjE2MjIyN30.EXkeCHuqA93MSTbkAoNJU06qsbQcoBRPnH6RZYEOYvo",
                               description="Refresh access token, use this to refresh the access token above in /authentications/refresh path")
    token_type:str = Field(..., example="bearer")
    expires_in: int = Field(..., description="Time until access token expires (in seconds)", example=3600)
    scope: Optional[str] = Field(None, description="Authorize list of actions", example="create")


class AccessToken(UserResponse):
    id: str
    iat: datetime
    exp: datetime


class RefreshToken(AutoCamelModel):
    session_id: str
    user_id: str
    iat: datetime


class RefreshTokenBody(AutoCamelModel):
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uX2lkIjoiOWEwYmFlZDMtMzMwMy00MjczLTkzYjYtM2NiMjUzOGI1MjdjIiwidXNlcl9pZCI6IjM3YjVlNjU4LWM3NjUtNGYyZC1hNWEwLWJjNjgwNWZjY2ZhYiIsImlhdCI6MTY1MjE2MjIyN30.EXkeCHuqA93MSTbkAoNJU06qsbQcoBRPnH6RZYEOYvo",
                               description="Refresh token gained from response after login")


class RefreshTokenResponseData(AutoCamelModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImYzZjYxZWQ4LTNhMDYtNDhlNi05NGE4LTkzZTU2ZDg0YjI5NiIsImVtYWlsIjoiZGFmYUBnbWFpbC5jb20iLCJwaG9uZSI6Iis2MjgxMzI5MDgyMzE0czEiLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY1MjEwMjk5MCwiaWF0IjoxNjUyMTAyMDkwfQ.SyhCaUvvvB7jMk5T7dEsGScHy6Pe5FqZhIkBEnJggT0", description=f"JWT access token that will expire in {settings.jwt_access_token_expiry_minutes} minutes")


class RefreshTokenResponse(ResponseTemplate):
    data: RefreshTokenResponseData
