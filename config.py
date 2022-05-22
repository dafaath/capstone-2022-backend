from enum import Enum
from pydantic import BaseSettings
from functools import lru_cache
import os


# Change this value if running on your own machine
# Database is currently using postgresql

class RunningENV(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"
    TEST_PRODUCTION = "test-production"


class DefaultSettings(BaseSettings):
    env: RunningENV = RunningENV.DEVELOPMENT
    db_user: str = "postgres"
    db_pass: str = ""
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "emodiary"
    db_unix_socket: str = ""
    admin_email: str = "admin@gmail.com"
    admin_password: str = "123"
    admin_phone_number: str = "+6281390494881"
    test_account_email: str = "test@gmail.com"
    test_account_password: str = "123"
    test_account_phone_number: str = "+6281392341928"
    jwt_access_token_secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    jwt_refresh_token_secret_key: str = ".W,='ht^xGH'Kg5j?b~5cG=Bh~G;Mr&rgUd4|KKtMEiB3IWjx:xD,!vJ&GxIMJMmNX>+WC~Oa6.p^wdOot"
    jwt_access_token_expiry_minutes: int = 60
    jwt_algorithm: str = "HS256"
    google_client_id: str = "137562844094-8v9i3tc76635h2hrm7kk0f2dg7sodnkk.apps.googleusercontent.com"
    google_cloud_project_id: str = "emodiary-bangkit"
    google_application_credentials = "service-account.json"  # Google cloud service account
    bucket_name: str = "emodiary-profile-picture"
    static_file_routes: str = "https://storage.googleapis.com/emodiary-profile-picture/"
    production_base_url: str = "https://emodiary-bangkit.et.r.appspot.com"

    class Config:
        use_enum_values = True


class DevSettings(DefaultSettings):
    pass


class TestSettings(DefaultSettings):
    env: RunningENV = RunningENV.TEST
    db_name: str = "test_emodiary"
    google_cloud_project_id: str = "emodiary-test"
    google_application_credentials = "service-account-test.json"  # Google cloud service account
    bucket_name: str = "emodiary-profile-picture-test"
    static_file_routes: str = "https://storage.googleapis.com/emodiary-profile-picture-test/"


class TestProductionSettings(TestSettings):
    env: RunningENV = RunningENV.TEST_PRODUCTION

    class Config:
        env_file = 'prod.env'
        env_file_encoding = 'utf-8'
        use_enum_values = True


class ProdSettings(DefaultSettings):
    env: RunningENV = RunningENV.PRODUCTION

    class Config:
        env_file = 'prod.env'
        env_file_encoding = 'utf-8'
        use_enum_values = True


@lru_cache()
def get_settings():
    if(os.environ.get("ENV") == RunningENV.DEVELOPMENT.value):
        return DevSettings()
    elif(os.environ.get("ENV") == RunningENV.TEST.value):
        return TestSettings()
    elif(os.environ.get("ENV") == RunningENV.TEST_PRODUCTION.value):
        return TestProductionSettings()
    elif(os.environ.get("ENV") == RunningENV.PRODUCTION.value):
        return ProdSettings()
    else:
        return DefaultSettings()
