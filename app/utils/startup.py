import json
import os

from aiofile import async_open
from sqlalchemy.orm import Session

from app import logger
from app.database import engine
from app.models import Base, UserRole
from app.schema.user import RegisterBody
from app.services.user import get_user_by_email, register_user
from config import DefaultSettings, RunningENV


async def generate_database_test(settings: DefaultSettings):
    # ! Danger this will drop the database, only do it in testing !
    if settings.env == RunningENV.TEST.value:
        logger.info("Dropping database...")
        Base.metadata.drop_all(bind=engine)
        logger.info("Creating database...")
        Base.metadata.create_all(bind=engine)
        logger.info("Finish creating")


async def create_account(settings: DefaultSettings, db: Session, type: str):
    user = get_user_by_email(settings.test_account_email, db)
    if type == "admin":
        user = get_user_by_email(settings.admin_email, db)
    if user:
        logger.info(f"{type.capitalize()} user already created")
    else:
        data = RegisterBody(
            email=settings.test_account_email,
            fullname="Test User",
            password=settings.test_account_password)
        if type.lower() == "admin":
            data = RegisterBody(
                email=settings.admin_email,
                fullname="admin bin admin",
                password=settings.admin_password)

        user_role = UserRole.REGULAR
        if type.lower() == "admin":
            user_role = UserRole.ADMIN
        user = register_user(data, db, user_role)
        logger.info(f"{type.capitalize()} user is created")

    if settings.env == RunningENV.TEST.value or settings.env == RunningENV.DEVELOPMENT.value:
        logger.info(
            f"email={user.email}, password={settings.admin_password}, phone_number={user.phone}")

    return user


async def create_test_account_if_not_exists(settings: DefaultSettings, db: Session):
    user = await create_account(settings, db, "test")
    return user


async def create_admin_account_if_not_exists(settings: DefaultSettings, db: Session):
    user = await create_account(settings, db, "admin")
    return user


async def write_openapi_file(settings: DefaultSettings, openapi):
    # If settings is production, don't create it
    if settings.env != RunningENV.TEST.value and settings.env != RunningENV.DEVELOPMENT.value:
        return

    # Write API
    logger.info("Creating openapi file")
    filename = 'openapi.json'
    full_path_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', filename)
    async with async_open(full_path_filename, 'w+') as afp:
        await afp.write(json.dumps(openapi))
        logger.info("Finish creating openapi file to " + full_path_filename)
