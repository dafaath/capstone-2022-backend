from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import get_settings
from google.cloud import firestore


settings = get_settings()
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# The `project` parameter is optional and represents which project the client
# will act on behalf of. If not supplied, the client falls back to the default
# project inferred from the environment.
import os


def get_fs():
    credentials = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               '..', settings.google_application_credentials)
    fs = firestore.Client(project=settings.google_cloud_project_id, credentials=credentials)
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
