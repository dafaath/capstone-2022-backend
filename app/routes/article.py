from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from google.cloud.firestore import Client
from pydantic import parse_obj_as

from app.database import get_fs
from app.schema.article import Article, GetAllArticleResponse
from app.schema.authentication import AccessToken
from app.schema.default_response import error_reason
from app.schema.diary import EmotionCategory
from app.services.article import get_all_articles
from app.utils.depedencies import get_current_user
from app.utils.schema import convert_enum_to_string
from config import get_settings

router = APIRouter(prefix="/articles",
                   tags=["Article"])
settings = get_settings()


@ router.get("/",
             description="Get articles from database, the response format is using serpapi example, https://serpapi.com/",
             status_code=200,
             response_model=GetAllArticleResponse,
             responses={403: error_reason("Only user with role admin can access this resource.")})
def get_all_diary_route(
        page: Optional[int] = Query(
            None,
            gt=0,
            description="Page of the pagination"),
        size: Optional[int] = Query(
            None,
            gt=0,
            description="The content size per page"),
        emotions: Optional[List[EmotionCategory]] = Query(
            None,
            description="The emotion related to the article, possible values: " +
            convert_enum_to_string(EmotionCategory)),
        current_user: AccessToken = Depends(get_current_user),
        fs: Client = Depends(get_fs)):
    articles = get_all_articles(fs, page=page, size=size, emotions=emotions)
    articles_response = parse_obj_as(list[Article], articles)
    response = GetAllArticleResponse(
        message="Successfully get articles from database", data=articles_response)
    return response
