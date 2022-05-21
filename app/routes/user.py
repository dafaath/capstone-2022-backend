from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Path, UploadFile
from google.cloud.storage import Bucket
from pydantic import parse_obj_as
from sqlalchemy.orm import Session

from app.database import get_bucket, get_db
from app.models import UserRole
from app.schema.authentication import AccessToken
from app.schema.default_response import error_reason
from app.schema.user import (DeleteUserResponse, GetAllUserResponse,
                             GetOneUserResponse, RegisterBody,
                             RegisterResponse, SaveUserPhotoResponse,
                             UpdateUserBody, UpdateUserResponse, UserResponse)
from app.services.user import (delete_user, get_all_user, get_user_by_email,
                               get_user_by_id, get_user_by_id_or_error,
                               register_user, save_user_profile_picture,
                               update_user)
from app.utils.depedencies import get_admin, get_current_user
from config import get_settings

router = APIRouter(prefix="/users",
                   tags=["User"])
settings = get_settings()


@ router.post("/", description="Register new user", status_code=201, tags=["Authentication"],
              response_model=RegisterResponse, responses={409: error_reason("Email is already exists in db")})
def register(body: RegisterBody, db: Session = Depends(get_db)):
    saved_user = register_user(body, db)
    response = RegisterResponse(
        message="Registration successful", data=UserResponse.from_orm(saved_user))
    return response


@ router.post("/{user_id}/photo",
              description="Upload user profile picture",
              status_code=201,
              response_model=SaveUserPhotoResponse,
              responses={422: error_reason("The file type is not image"),
                         403: error_reason("The user id in bearer is not matching with path and the user is not admin")})
def save_user_picture_route(
        file: UploadFile = File(..., description="The new user profile picture, must be in png, jpeg, or jpg format"),
        user_id: UUID = Path(...,
                             description="The user id in UUID format"),
        current_user: AccessToken = Depends(get_current_user),
        bucket: Bucket = Depends(get_bucket),
        db: Session = Depends(get_db)):
    if current_user.id != str(user_id) and current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "The user id in token and path is not matching",
                            headers={"WWW-Authenticate": "Bearer"})

    user = get_user_by_id_or_error(str(user_id), db)
    user = save_user_profile_picture(user, file, bucket, db)
    response = SaveUserPhotoResponse(
        message="Successfully change the user profile picture", data=UserResponse.from_orm(user))
    return response


@ router.get("/", description="Get all users", status_code=200, response_model=GetAllUserResponse,
             responses={403: error_reason("Only user with role admin can access this resource.")})
def get_all_user_route(current_user: AccessToken = Depends(get_admin), db: Session = Depends(get_db)):
    users = get_all_user(db)
    users_response = parse_obj_as(list[UserResponse], users)
    response = GetAllUserResponse(
        message="Successfully get all users", data=users_response)
    return response


@ router.get("/{user_id}", description="Get users by id", status_code=200, response_model=GetOneUserResponse,
             responses={403: error_reason("The user id in bearer is not matching with path and the user is not admin")})
def get_one_user_route(
        user_id: UUID = Path(...,
                             description="The user id in UUID format"),
        current_user: AccessToken = Depends(get_current_user),
        db: Session = Depends(get_db)):
    if current_user.id != str(user_id) and current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "The user id in token and path is not matching",
                            headers={"WWW-Authenticate": "Bearer"})

    user = get_user_by_id_or_error(str(user_id), db)
    response = GetOneUserResponse(
        message="Successfully get user", data=UserResponse.from_orm(user))
    return response


@ router.patch("/{user_id}", description="Update user data", status_code=201, response_model=UpdateUserResponse,
               responses={403: error_reason("The user id in bearer is not matching with path and the user is not admin")})
def update_user_route(
        body: UpdateUserBody,
        user_id: UUID = Path(...,
                             description="The user id in UUID format"),
        current_user: AccessToken = Depends(get_current_user),
        db: Session = Depends(get_db)):
    if current_user.id != str(user_id) and current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "The user id in token and path is not matching",
                            headers={"WWW-Authenticate": "Bearer"})

    user = get_user_by_id_or_error(str(user_id), db)
    updated_user = update_user(user, body, db)

    response = UpdateUserResponse(
        message="Successfully update user", data=UserResponse.from_orm(updated_user))
    return response


@ router.delete("/{user_id}", description="Delete user data", status_code=200, response_model=DeleteUserResponse,
                responses={403: error_reason("The user id in bearer is not matching with path and the user is not admin")})
def delete_user_route(
        user_id: UUID = Path(...,
                             description="The user id in UUID format"),
        current_user: AccessToken = Depends(get_current_user),
        db: Session = Depends(get_db)):
    if current_user.id != str(user_id) and current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "The user id in token and path is not matching",
                            headers={"WWW-Authenticate": "Bearer"})

    user = get_user_by_id_or_error(str(user_id), db)
    deleted_user = delete_user(user, db)

    response = DeleteUserResponse(
        message="Successfully delete user", data=UserResponse.from_orm(deleted_user))
    return response
