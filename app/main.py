from fastapi import FastAPI

from app.routes import authentication
from app.utils.response import ResponseTemplate
from app.database import engine, Base
from app.models.authentication import Item, User
from config import get_settings

settings = get_settings()

# if settings.env == "development":
#     print("Creating database...")
#     Base.metadata.create_all(bind=engine)
#     print("Finish creating")

app = FastAPI(title="emodiary API")
app.include_router(authentication.router)


@app.get("/", tags=["Health Check"], status_code=200, response_model=ResponseTemplate)
def health_check():
    return ResponseTemplate(status=200, message="Server is ok")
