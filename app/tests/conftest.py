import asyncio

import pytest
from google.cloud.firestore import Client
from google.cloud.storage import Bucket
from sqlalchemy.orm import Session, close_all_sessions

from app.database import Base, engine, get_bucket, get_db, get_fs
from app.schema.user import UserResponse
from app.services.authentication import create_access_token
from app.services.user import get_user_by_email
from app.utils.conftest_utils import delete_all_collection, delete_all_object
from app.utils.startup import (create_admin_account_if_not_exists,
                               create_test_account_if_not_exists)
from config import DefaultSettings, get_settings

pytest.register_assert_rewrite("app.utils.test")


@pytest.fixture(scope="session")
async def test_db():
    print("Creating test database")
    db: Session = next(get_db())
    fs: Client = next(get_fs())
    bucket: Bucket = next(get_bucket())
    settings: DefaultSettings = get_settings()
    Base.metadata.create_all(bind=engine)
    await create_admin_account_if_not_exists(settings, db)
    await create_test_account_if_not_exists(settings, db)
    yield
    print("Dropping test database")
    # delete_all_object(bucket)
    delete_all_collection(fs)
    close_all_sessions()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def admin():
    db: Session = next(get_db())
    settings: DefaultSettings = get_settings()
    user = get_user_by_email(settings.admin_email, db)
    yield user
    print("Closing database")
    close_all_sessions()


@pytest.fixture(scope="session")
def user():
    db: Session = next(get_db())
    settings: DefaultSettings = get_settings()
    user = get_user_by_email(settings.test_account_email, db)
    yield user
    print("Closing database")
    close_all_sessions()


@pytest.fixture(scope="session")
def user_token():
    db: Session = next(get_db())
    settings: DefaultSettings = get_settings()
    user = get_user_by_email(settings.test_account_email, db)
    access_token = create_access_token(UserResponse.from_orm(user))
    yield access_token
    print("Closing database")
    close_all_sessions()


@pytest.fixture(scope="session")
def admin_token():
    db: Session = next(get_db())
    settings: DefaultSettings = get_settings()
    user = get_user_by_email(settings.admin_email, db)
    access_token = create_access_token(UserResponse.from_orm(user))
    yield access_token
    print("Closing database")
    close_all_sessions()


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
