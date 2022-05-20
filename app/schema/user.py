from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field

from app.models import UserRole
from app.schema.default_response import ResponseTemplate
from app.utils.schema import TemplateModel


class RegisterBase(TemplateModel):
    email: EmailStr = Field(..., example="example@gmail.com",
                            description="User email")
    fullname: str = Field(..., example="James Jones", description="User full name")


class RegisterBody(RegisterBase):
    password: str = Field(..., description="User password")


class UserResponse(RegisterBase):
    id: UUID = Field(..., description="User id in UUID format")
    phone: Optional[str] = Field(
        None,
        example="+6281390823143",
        regex=r"\+[\d]{8,15}",
        description="User telephone number with country code in front, with a 8-15 character length")
    is_active: bool = Field(..., description="Is user is an active user or not")
    photo: str = Field(..., description="The path to the user photo profile")
    time_created: datetime = Field(..., description="The time this object is created, represented in ISO 8601 format",
                                   example="2022-05-12T14:30:28.304902+07:00")
    time_updated: datetime = Field(...,
                                   description="The time this object is last updated, represented in ISO 8601 format ",
                                   example="2022-05-12T14:30:28.304902+07:00")
    role: UserRole = Field(..., description=f"The user role, consist of {UserRole}.")


class RegisterResponse(ResponseTemplate):
    data: UserResponse


class GetAllUserResponse(ResponseTemplate):
    data: list[UserResponse]


class GetOneUserResponse(ResponseTemplate):
    data: UserResponse


class UpdateUserBody(TemplateModel):
    email: Optional[EmailStr] = Field(None, example="example@gmail.com",
                                      description="User email")
    phone: Optional[str] = Field(
        None,
        example="+6281390823143",
        regex=r"\+[\d]{8,15}",
        description="User telephone number with country code in front, with a 8-15 character length")
    current_password: Optional[str] = Field(None, description="The user current password")
    new_password: Optional[str] = Field(None, description="The user new password")


class UpdateUserResponse(ResponseTemplate):
    data: UserResponse


class DeleteUserResponse(ResponseTemplate):
    data: UserResponse
