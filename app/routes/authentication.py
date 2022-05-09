from datetime import timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schema.authentication import LoginBody, LoginResponse, LoginResponseData, Register, RegisterResponse, UserResponse
from app.services.authentication import create_access_token, login_user, register_user

router = APIRouter(prefix="/authentications",
                   tags=["Authentication"])


@ router.post("/register", status_code=201, response_model=RegisterResponse)
def register(body: Register, db: Session = Depends(get_db)):
    saved_user = register_user(body, db)
    response = RegisterResponse(
        status=201, message="Registration successful", data=UserResponse.from_orm(saved_user))
    return response


@ router.post("/login", status_code=200, response_model=LoginResponse)
def login(body: LoginBody, db: Session = Depends(get_db)):
    user = login_user(body, db)

    # Create access token that will expire in 15 minutes
    access_token = create_access_token(
        UserResponse.from_orm(user), timedelta(minutes=15))

    response = LoginResponse(
        status=201, message="Login successful", data=LoginResponseData(access_token=access_token))
    return response
