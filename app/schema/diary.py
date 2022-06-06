
import enum
from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schema.default_response import ResponseTemplate
from app.schema.user import UserResponse
from app.utils.schema import TemplateModel, convert_enum_to_string


class EmotionCategory(enum.Enum):
    SADNESS = "sadness"
    JOY = "joy"
    ANGER = "anger"
    FEAR = "fear"
    LOVE = "love"
    SURPRISE = "surprise"


class ArticleLanguage(enum.Enum):
    ID = "id"
    EN = "en"


class DetectedExtensions(TemplateModel):
    skor: Optional[float]
    suara: Optional[int]
    langkah: Optional[int]


class Top(TemplateModel):
    detected_extensions: DetectedExtensions
    extensions: list[str]


class RichSnippet(TemplateModel):
    top: Top


class ArticleBase(TemplateModel):
    emotion: EmotionCategory = Field(..., description="The emotion category from ML, possible value: " +
                                     convert_enum_to_string(EmotionCategory))
    language: ArticleLanguage = Field(..., description="The language of the article, possible value: " +
                                      convert_enum_to_string(ArticleLanguage))
    position: int = Field(..., description="The result position in google search, lower is top")
    title: str
    link: str
    displayed_link: str
    snippet: Optional[str]
    snippet_highlighted_words: Optional[list[str]]
    date: Optional[str]
    rich_snippet: Optional[RichSnippet]


class ArticleDatabase(ArticleBase):
    pass


class Article(ArticleBase):
    id: str = Field(..., description="Article id in UUID format")


class BaseDiary(TemplateModel):
    title: str = Field(..., description="The diary title")
    content: str = Field(..., description="The diary content")


class DiaryResponseBase(BaseDiary):
    id: str = Field(..., description="Diary id in UUID format")
    translated_content: str = Field(...,
                                    description="The diary content in english after translating with google translate")
    emotion: EmotionCategory = Field(
        ...,
        description="Diary emotion based on machine learning output, possible values: " +
        convert_enum_to_string(EmotionCategory))
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


class GetEmotionSummaryResponseData(TemplateModel):
    emotion: Optional[EmotionCategory] = Field(
        ...,
        description="The summary of 10 last diary emotion, possible values: Null (if there is no diary yet) or" +
        convert_enum_to_string(EmotionCategory))


class GetEmotionSummaryResponse(ResponseTemplate):
    data: GetEmotionSummaryResponseData


class DiaryResponseWithoutUserPlusArticles(DiaryResponseWithoutUser):
    articles: list[Article] = Field(
        ...,
        description="List of articles based on this diary emotion. Positive emotion don't have articles in them, this is represented by empty array")


class DiaryDatabase(DiaryResponseBase):
    pass


class CreateDiaryBody(BaseDiary):
    pass


class CreateDiaryResponse(ResponseTemplate):
    data: DiaryResponseWithoutUserPlusArticles


class GetAllDiaryResponse(ResponseTemplate):
    data: list[DiaryResponseWithoutUser]


class GetOneDiaryResponse(ResponseTemplate):
    data: DiaryResponseWithoutUser


class UpdateDiaryBody(CreateDiaryBody):
    title: Optional[str] = Field(None, description="The diary title")
    content: Optional[str] = Field(None, description="The diary content")


class UpdateDiaryResponse(ResponseTemplate):
    data: DiaryResponseWithoutUserPlusArticles


class DeleteDiaryResponse(ResponseTemplate):
    data: DiaryResponseWithoutUser


class TranslateResponse(TemplateModel):
    translated_text: str
    detected_source_language: str
    input: str


class GetAllArticleResponse(ResponseTemplate):
    data: list[Article]
