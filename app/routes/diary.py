from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from google.cloud.firestore import Client
from pydantic import parse_obj_as
from sqlalchemy.orm import Session

from app.database import get_db, get_fs
from app.models import User, UserRole
from app.schema.authentication import AccessToken
from app.schema.default_response import error_reason
from app.schema.diary import (CreateDiaryBody, CreateDiaryResponse,
                              DeleteDiaryResponse, DiaryResponseWithoutUser,
                              DiaryResponseWithUser, GetAllDiaryResponse,
                              GetOneDiaryResponse, UpdateDiaryBody,
                              UpdateDiaryResponse)
from app.schema.user import UserResponse
from app.services.diary import (create_diary, delete_diary, get_all_diary,
                                get_diary_by_id, get_diary_by_id_or_error, get_user_diary,
                                update_diary)
from app.services.user import get_user_by_id_or_error
from app.utils.depedencies import get_admin, get_current_user
from config import get_settings

router = APIRouter(prefix="/diaries",
                   tags=["Diary"])
settings = get_settings()


@ router.post("/",
              description="Create new diary",
              status_code=201,
              response_model=CreateDiaryResponse)
def create_diary_route(body: CreateDiaryBody, fs: Client = Depends(get_fs),
                       db: Session = Depends(get_db),
                       current_user: AccessToken = Depends(get_current_user)):
    user = get_user_by_id_or_error(current_user.id, db)
    saved_diary = create_diary(body, user, fs)
    data = DiaryResponseWithoutUser(**saved_diary.dict())
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
        diary_id: UUID = Path(...,
                              description="The diary id in UUID format"),
        current_user: AccessToken = Depends(get_current_user),
        fs: Client = Depends(get_fs)):

    diary = get_diary_by_id_or_error(str(diary_id), fs)

    if current_user.id != diary.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "You are not allowed do this action because you are not the owner of this diary.",
                            headers={"WWW-Authenticate": "Bearer"})

    updated_diary = update_diary(diary, body, fs)

    data = DiaryResponseWithoutUser(**updated_diary.dict())
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
