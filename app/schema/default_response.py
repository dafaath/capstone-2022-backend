from pydantic import Field

from app.utils.schema import AutoCamelModel


class ResponseTemplate(AutoCamelModel):
    status: int = Field(example=200, description="Response status code")
    message: str = Field(example="Server is ok",
                         description="Message from server")
    data: dict = Field(description="Response data")
