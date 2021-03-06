import os

from google.cloud import firestore, storage
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app import logger
from config import RunningENV, get_settings

settings = get_settings()
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}"


if settings.env == RunningENV.PRODUCTION.value:
    SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.db_user}:{settings.db_pass}@/{settings.db_name}?host=/cloudsql/{settings.db_unix_socket}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
logger.info(
    f"Connecting to database postgresql on {settings.db_host}:{settings.db_port} connected to {settings.db_name}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


credentials_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                '..', settings.google_application_credentials)
credentials = service_account.Credentials.from_service_account_file(
    credentials_file)
project = settings.google_cloud_project_id


def get_translate_client():
    translate_client = translate.Client(credentials=credentials)
    try:
        yield translate_client
    finally:
        pass


def get_bucket():
    storage_client = storage.Client(project=project, credentials=credentials)
    bucket = storage_client.get_bucket(settings.bucket_name)
    try:
        yield bucket
    finally:
        pass


def get_fs():
    fs = firestore.Client(project=project, credentials=credentials)
    try:
        yield fs
    finally:
        fs.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
