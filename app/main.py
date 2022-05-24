import asyncio

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import get_db
from app.routes import article, authentication, diary, example, user
from app.schema.default_response import (HTTPErrorResponseTemplate,
                                         ResponseTemplate, error_reason)
from app.utils.startup import (create_admin_account_if_not_exists,
                               create_test_account_if_not_exists,
                               generate_database_test, write_openapi_file)
from config import DefaultSettings, get_settings

app = FastAPI(responses={400: error_reason("Request error")})
app.include_router(authentication.router)
app.include_router(diary.router)
app.include_router(user.router)
app.include_router(article.router)
app.include_router(example.router)

# CORS
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(HTTPErrorResponseTemplate(message=exc.detail)),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    error_detail = f"{exc.errors()[0]['loc'][1]} {exc.errors()[0]['msg']}"
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder(HTTPErrorResponseTemplate(message=error_detail)),
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Emodiary API",
        version="1.0.0",
        description="Emodiary backend api for capstone project in Bangkit 2022",
        routes=app.routes,
    )
    methods = ["get", "post", "put", "delete", "patch"]
    # look for the error 422 and removes it
    for path in openapi_schema["paths"]:
        for method in methods:
            print(path, method)
            try:
                del openapi_schema["paths"][path][method]["responses"]["422"]
            except KeyError:
                pass

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.on_event("startup")
async def startup():
    db: Session = next(get_db())
    settings: DefaultSettings = get_settings()
    asyncio.create_task(generate_database_test(settings))
    asyncio.create_task(create_admin_account_if_not_exists(settings, db))
    asyncio.create_task(create_test_account_if_not_exists(settings, db))
    asyncio.create_task(write_openapi_file(settings, app.openapi()))


@app.get("/", tags=["Health Check"], status_code=200, response_model=ResponseTemplate)
def health_check():
    return ResponseTemplate(message="Server is ok")
