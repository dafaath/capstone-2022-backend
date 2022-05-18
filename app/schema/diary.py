from datetime import datetime
from doctest import Example
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field, validator

from app.schema.default_response import ResponseTemplate
from app.schema.user import UserResponse
from app.utils.schema import TemplateModel


class BaseDiary(TemplateModel):
    content: str = Field(..., description="The diary content")


class DiaryResponseBase(BaseDiary):
    id: str = Field(..., description="Diary id in UUID format")
    translated_content: str = Field(...,
                                    description="The diary content in english after translating with google translate")
    emotion: str = Field(..., description="Diary emotion based on machine learning output")
    user_id: str = Field(..., description="The user id in UUID format that owns this diary")
    time_created: datetime = Field(..., description="The time this object is created, represented in ISO 8601 format",
                                   example="2022-05-12T14:30:28.304902+07:00")
    time_updated: datetime = Field(...,
                                   description="The time this object is last updated, represented in ISO 8601 format",
                                   example="2022-05-12T14:30:28.304902+07:00")


class DiaryResponseWithUser(DiaryResponseBase):
    user: UserResponse = Field(..., description="The user object that owns this diary")


class DiaryResponseWithoutUser(DiaryResponseBase):
    pass


class CreateDiaryBody(BaseDiary):
    pass


class DiaryDatabase(DiaryResponseBase):
    pass


class CreateDiaryResponse(ResponseTemplate):
    data: DiaryResponseWithUser


class CreateDiaryResponse(ResponseTemplate):
    data: DiaryResponseWithUser


class GetAllDiaryResponse(ResponseTemplate):
    data: list[DiaryResponseWithoutUser]


class GetOneDiaryResponse(ResponseTemplate):
    data: DiaryResponseWithUser


class UpdateDiaryBody(CreateDiaryBody):
    pass


class UpdateDiaryResponse(ResponseTemplate):
    data: DiaryResponseWithUser


class DeleteDiaryResponse(ResponseTemplate):
    data: DiaryResponseWithUser