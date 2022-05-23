
from pydantic import Field, validator

from app.utils.schema import TemplateModel


class ResponseTemplate(TemplateModel):
    message: str = Field(example="Server is ok",
                         description="Message from server")
    data: dict = Field(None, description="Response data")


class HTTPErrorResponseTemplate(TemplateModel):
    message: str = Field(...,
                         description="The reason for the error", example="error reasons")

    @validator('message')
    def capitalize_string(cls, v: str):
        return v.capitalize()


def error_reason(description: str):
    return {"model": HTTPErrorResponseTemplate, "description": description}
