from fastapi import APIRouter

from app.utils.response import ResponseTemplate

router = APIRouter(prefix="/authentications", tags=["Authentication"])


@router.post("/register", status_code=201)
def register():
    return ResponseTemplate(201, "Registration successful")
