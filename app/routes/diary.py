from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from google.cloud.firestore import Client
from google.cloud.translate_v2 import Client as TranslateClient
from pydantic import parse_obj_as
from sqlalchemy.orm import Session

from app.database import get_db, get_fs, get_translate_client
from app.dependencies import get_model, get_tokenizer
from app.models import UserRole
from app.schema.authentication import AccessToken
from app.schema.default_response import error_reason
from app.schema.diary import (CreateDiaryBody, CreateDiaryResponse,
                              DeleteDiaryResponse, DiaryResponseWithoutUser,
                              DiaryResponseWithoutUserPlusArticles,
                              EmotionCategory, GetAllDiaryResponse,
                              GetEmotionSummaryResponse,
                              GetEmotionSummaryResponseData,
                              GetOneDiaryResponse, UpdateDiaryBody,
                              UpdateDiaryResponse)
from app.services.article import get_all_articles
from app.services.diary import (create_diary, delete_diary, get_all_diary,
                                get_diary_by_id_or_error, get_emotion_summary,
                                get_user_diary, update_diary)
from app.utils.depedencies import get_admin, get_current_user
from config import get_settings

router = APIRouter(prefix="/diaries",
                   tags=["Diary"])
settings = get_settings()


@ router.post("/",
              description="Create new diary",
              status_code=201,
              response_model=CreateDiaryResponse)
def create_diary_route(
        body: CreateDiaryBody,
        translate: Optional[bool] = Query(
            True,
            description="Set false for testing purposes only (so it can limit the translate cost)"),
        emotion: Optional[EmotionCategory] = Query(
            None,
            description="Force set an emotion to this diary, use for testing purposes only"),
        fs: Client = Depends(get_fs),
        db: Session = Depends(get_db),
        tokenizer=Depends(get_tokenizer),
        model=Depends(get_model),
        translate_client: TranslateClient = Depends(get_translate_client),
        current_user: AccessToken = Depends(get_current_user)):
    saved_diary = create_diary(
        body,
        current_user.id,
        fs,
        translate_client,
        translate=translate,
        emotion=emotion,
        tokenizer=tokenizer,
        model=model)
    articles = get_all_articles(fs, page=1, size=10, emotions=[saved_diary.emotion])
    data = DiaryResponseWithoutUserPlusArticles(**saved_diary.dict(), articles=articles)
    response = CreateDiaryResponse(
        message="Create diary successful", data=data)
    return response


@ router.get("/all", description="Get all diaries from database", status_code=200, response_model=GetAllDiaryResponse,
             responses={403: error_reason("Only user with role admin can access this resource.")})
def get_all_diary_route(page: Optional[int] = Query(None,
                                                    gt=0,
                                                    description="Page of the pagination"),
                        size: Optional[int] = Query(None,
                                                    gt=0,
                                                    description="The content size per page"),

                        current_user: AccessToken = Depends(get_admin), fs: Client = Depends(get_fs)):
    diaries = get_all_diary(page, size, fs)
    diaries_response = parse_obj_as(list[DiaryResponseWithoutUser], diaries)
    response = GetAllDiaryResponse(
        message="Successfully get all diaries in database", data=diaries_response)
    return response


@ router.get("/emotions",
             description="Get emotion from the last 10 diary",
             status_code=200,
             response_model=GetEmotionSummaryResponse)
def get_emotion_summary_route(current_user: AccessToken = Depends(get_current_user), fs: Client = Depends(get_fs)):
    page = 1
    size = 10
    diaries = get_user_diary(page, size, current_user.id, fs)
    emotion = get_emotion_summary(diaries)
    response = GetEmotionSummaryResponse(
        message="Successfully get emotion summary for " +
        current_user.fullname,
        data=GetEmotionSummaryResponseData(
            emotion=emotion))
    return response


@ router.get("/", description="Get YOUR diary", status_code=200, response_model=GetAllDiaryResponse)
def get_user_diary_route(page: Optional[int] = Query(None,
                                                     gt=0,
                                                     description="Page of the pagination"),
                         size: Optional[int] = Query(None,
                                                     gt=0,
                                                     description="The content size per page"),
                         current_user: AccessToken = Depends(get_current_user),
                         fs: Client = Depends(get_fs)):
    diaries = get_user_diary(page, size, current_user.id, fs)
    diaries_response = parse_obj_as(list[DiaryResponseWithoutUser], diaries)
    response = GetAllDiaryResponse(
        message="Successfully get all diaries for user " + current_user.fullname, data=diaries_response)
    return response


@ router.get("/{diary_id}",
             description="Get diaries by id",
             status_code=200,
             response_model=GetOneDiaryResponse,
             response_model_exclude_unset=True,
             responses={403: error_reason("The user id in bearer is not matching with path and the user is not admin")})
def get_one_diary_route(
        diary_id: UUID = Path(...,
                              description="The diary id in UUID format"),
        current_user: AccessToken = Depends(get_current_user),
        fs: Client = Depends(get_fs)):

    diary = get_diary_by_id_or_error(str(diary_id), fs)

    if current_user.id != diary.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "You are not allowed do this action because you are not the owner of this diary.",
                            headers={"WWW-Authenticate": "Bearer"})

    data = DiaryResponseWithoutUser(**diary.dict())
    response = GetOneDiaryResponse(
        message="Successfully get diary", data=data)
    return response


@ router.patch("/{diary_id}", description="Update diary data", status_code=201, response_model=UpdateDiaryResponse,
               responses={403: error_reason("The user id in bearer is not matching with path and the user is not admin")})
def update_diary_route(
        body: UpdateDiaryBody,
        translate: Optional[bool] = Query(
            True,
            description="Set false for testing purposes only (so it can limit the translate cost)"),
        diary_id: UUID = Path(...,
                              description="The diary id in UUID format"),
        translate_client: TranslateClient = Depends(get_translate_client),
        current_user: AccessToken = Depends(get_current_user),
        tokenizer=Depends(get_tokenizer),
        model=Depends(get_model),
        fs: Client = Depends(get_fs)):

    diary = get_diary_by_id_or_error(str(diary_id), fs)

    if current_user.id != diary.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "You are not allowed do this action because you are not the owner of this diary.",
                            headers={"WWW-Authenticate": "Bearer"})

    updated_diary = update_diary(diary, body, fs, tokenizer, model, translate_client, translate)
    articles = get_all_articles(fs, page=1, size=10, emotions=[updated_diary.emotion])

    data = DiaryResponseWithoutUserPlusArticles(**updated_diary.dict(), articles=articles)
    response = UpdateDiaryResponse(
        message="Successfully update diary", data=data)
    return response


@ router.delete("/{diary_id}", description="Delete diary data", status_code=200, response_model=DeleteDiaryResponse,
                responses={403: error_reason("The user id in bearer is not matching with path and the user is not admin")})
def delete_diary_route(
        diary_id: UUID = Path(...,
                              description="The diary id in UUID format"),
        current_user: AccessToken = Depends(get_current_user),
        fs: Client = Depends(get_fs)):

    diary = get_diary_by_id_or_error(str(diary_id), fs)

    if current_user.id != diary.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "You are not allowed do this action because you are not the owner of this diary.",
                            headers={"WWW-Authenticate": "Bearer"})

    deleted_diary = delete_diary(diary, fs)

    data = DiaryResponseWithoutUser(**deleted_diary.dict())
    response = DeleteDiaryResponse(
        message="Successfully delete diary", data=data)
    return response
