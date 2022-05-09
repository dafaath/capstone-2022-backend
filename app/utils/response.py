from pydantic import BaseModel, Field


class ResponseTemplate(BaseModel):
    status: int = Field(example=200)
    message: str = Field(example="Server is ok")
    data: dict = None
