from fastapi import FastAPI
import logging
from logging.config import dictConfig

from app.routes import authentication
from app.schema.default_response import ResponseTemplate
from app.utils.logger import LogConfig
# from app.database import engine, Base
# from app.models.authentication import Item, User
from config import get_settings

settings = get_settings()
dictConfig(LogConfig().dict())
logger = logging.getLogger("default_logger")
logger.info(f"Starting application on {settings.env} environment")

# if settings.env == "development":
#     print("Creating database...")
#     Base.metadata.create_all(bind=engine)
#     print("Finish creating")

app = FastAPI(title="emodiary API", version="1.0.0")
app.include_router(authentication.router)


@app.get("/", tags=["Health Check"], status_code=200, response_model=ResponseTemplate)
def health_check():
    return ResponseTemplate(status=200, message="Server is ok")
