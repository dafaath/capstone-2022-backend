from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import HTMLResponse
from app import templates


router = APIRouter(prefix="/examples",
                   tags=["Examples"])


@router.get("/login", description="Example of login with google, this is a static html path", response_class=HTMLResponse)
async def login_google_example(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
