
import enum
from typing import List, Optional

from pydantic import Field

from app.schema.default_response import ResponseTemplate
from app.schema.diary import EmotionCategory
from app.utils.schema import TemplateModel, convert_enum_to_string


class ArticleLanguage(enum.Enum):
    ID = "id"
    EN = "en"


class DetectedExtensions(TemplateModel):
    skor: Optional[float]
    suara: Optional[int]
    langkah: Optional[int]


class Top(TemplateModel):
    detected_extensions: DetectedExtensions
    extensions: List[str]


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
    snippet_highlighted_words: Optional[List[str]]
    date: Optional[str]
    rich_snippet: Optional[RichSnippet]


class ArticleDatabase(ArticleBase):
    pass


class Article(ArticleBase):
    id: str = Field(..., description="Article id in UUID format")


class GetAllArticleResponse(ResponseTemplate):
    data: List[Article]
