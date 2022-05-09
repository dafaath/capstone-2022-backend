from doctest import Example
from uuid import UUID
from pydantic import Field, EmailStr
from app.models.authentication import User
from app.schema.default_response import ResponseTemplate
from app.utils.schema import AutoCamelModel


class Register(AutoCamelModel):
    email: EmailStr = Field(..., example="example@gmail.com",
                            description="User email")
    phone: str = Field(..., example="+6281390823143",
                       regex=r"\+[\d]{8,15}",
                       description="User telephone number with country code in front, with a 8-15 character length")
    password: str = Field(..., description="User password")


class UserResponse(AutoCamelModel):
    id: UUID = Field(..., description="User id in UUID format")
    email: EmailStr = Field(None, example="example@gmail.com",
                            description="User email")
    phone: str = Field(..., example="+6281390823143",
                       regex=r"\+[\d]{8,15}",
                       description="User telephone number with country code in front, with a 8-15 character length")
    is_active: bool = Field(
        ..., description="Is user is an active user or not")


class RegisterResponse(ResponseTemplate):
    data: UserResponse


class LoginBody(AutoCamelModel):
    email: EmailStr = Field(..., example="example@gmail.com",
                            description="User email")
    password: str = Field(..., description="User password")


class LoginResponseData(AutoCamelModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImYzZjYxZWQ4LTNhMDYtNDhlNi05NGE4LTkzZTU2ZDg0YjI5NiIsImVtYWlsIjoiZGFmYUBnbWFpbC5jb20iLCJwaG9uZSI6Iis2MjgxMzI5MDgyMzE0czEiLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY1MjEwMjk5MCwiaWF0IjoxNjUyMTAyMDkwfQ.SyhCaUvvvB7jMk5T7dEsGScHy6Pe5FqZhIkBEnJggT0", description="JWT access token")


class LoginResponse(ResponseTemplate):
    data: LoginResponseData
