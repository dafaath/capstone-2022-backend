from fastapi import FastAPI
from app import logger
from app.routes import authentication, example
from app.schema.default_response import ResponseTemplate
from app.database import engine, Base
from app.models.authentication import User
from aiofile import async_open

import json
import os
from config import get_settings

# Config settings
settings = get_settings()

# ! Danger this will drop the database, only do it in testing !
if settings.env == "test":
    logger.info("Dropping database...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Creating database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Finish creating")

app = FastAPI(title="emodiary API", version="1.0.0")
app.include_router(authentication.router)
app.include_router(example.router)


@app.on_event("startup")
async def startup():
    filename = 'openapi.json'
    full_path_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', filename)
    async with async_open(full_path_filename, 'w+') as afp:
        await afp.write(json.dumps(app.openapi()))


@app.get("/", tags=["Health Check"], status_code=200, response_model=ResponseTemplate)
def health_check():
    return ResponseTemplate(status=200, message="Server is ok")
