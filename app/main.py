import asyncio

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes import authentication, diary, example, user
from app.schema.default_response import ResponseTemplate
from app.utils.startup import (create_admin_account_if_not_exists,
                               generate_database_test, write_openapi_file)
from config import DefaultSettings, get_settings

app = FastAPI(title="emodiary API", version="1.0.0")
app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(diary.router)
app.include_router(example.router)


@app.on_event("startup")
async def startup():
    db: Session = next(get_db())
    settings: DefaultSettings = get_settings()
    asyncio.create_task(generate_database_test(settings))
    asyncio.create_task(create_admin_account_if_not_exists(settings, db))
    asyncio.create_task(write_openapi_file(app.openapi()))


@app.get("/", tags=["Health Check"], status_code=200, response_model=ResponseTemplate)
def health_check():
    return ResponseTemplate(message="Server is ok")
