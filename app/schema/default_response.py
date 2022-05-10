from doctest import Example
from pydantic import Field

from app.utils.schema import AutoCamelModel


class ResponseTemplate(AutoCamelModel):
    status: int = Field(example=200, description="Response status code")
    message: str = Field(example="Server is ok",
                         description="Message from server")
    data: dict = Field(None, description="Response data")


class MyHTTPError(AutoCamelModel):
    detail: str = Field(...,
                        description="The reason for the error", example="Error reasons")


def error_reason(description: str):
    return {"model": MyHTTPError, "description": description}
