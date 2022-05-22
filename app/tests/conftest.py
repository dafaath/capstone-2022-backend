import asyncio

import pytest
from google.cloud.firestore import Client
from google.cloud.storage import Bucket
from sqlalchemy.orm import Session, close_all_sessions

from app.database import Base, engine, get_bucket, get_db, get_fs
from app.utils.conftest_utils import (delete_all_collection, delete_all_object,
                                      get_client)
from app.utils.startup import (create_admin_account_if_not_exists,
                               create_test_account_if_not_exists)
from config import DefaultSettings, RunningENV, get_settings

pytest.register_assert_rewrite("app.utils.test")


@pytest.fixture(scope="session")
async def test_db():
    settings: DefaultSettings = get_settings()
    if settings.env != RunningENV.TEST_PRODUCTION.value:
        print("Creating test database")
        db: Session = next(get_db())
        fs: Client = next(get_fs())
        bucket: Bucket = next(get_bucket())
        Base.metadata.create_all(bind=engine)
        await create_admin_account_if_not_exists(settings, db)
        await create_test_account_if_not_exists(settings, db)
        yield
        print("Dropping test database")
        delete_all_object(bucket)
        delete_all_collection(fs)
        close_all_sessions()
        Base.metadata.drop_all(bind=engine)
    else:
        yield


@pytest.fixture(scope="session")
def user_token():
    settings: DefaultSettings = get_settings()
    client = get_client(settings)
    response = client.post("/authentications/login", data={
        "username": settings.test_account_email,
        "password": settings.test_account_password
    })
    resp = response.json()
    access_token = resp['access_token']
    yield access_token


@pytest.fixture(scope="session")
def admin_token():
    settings: DefaultSettings = get_settings()
    client = get_client(settings)
    response = client.post("/authentications/login", data={
        "username": settings.admin_email,
        "password": settings.admin_password
    })
    resp = response.json()
    access_token = resp['access_token']
    yield access_token


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def client():
    settings = get_settings()
    client = get_client(settings)
    yield client
