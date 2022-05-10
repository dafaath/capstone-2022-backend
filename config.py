from pydantic import BaseSettings
from functools import lru_cache
import os


# Change this value if running on your own machine
# Database is currently using postgresql
class DefaultSettings(BaseSettings):
    env: str = "development"
    db_user: str = "postgres"
    db_pass: str = ""
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "emodiary"
    jwt_access_token_secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    jwt_refresh_token_secret_key: str = ".W,='ht^xGH'Kg5j?b~5cG=Bh~G;Mr&rgUd4|KKtMEiB3IWjx:xD,!vJ&GxIMJMmNX>+WC~Oa6.p^wdOot"
    jwt_access_token_expiry_minutes: int = 60
    jwt_algorithm: str = "HS256"


class DevSettings(DefaultSettings):
    pass


class TestSettings(DefaultSettings):
    env: str = "test"
    db_name: str = "test_emodiary"


class ProdSettings(DefaultSettings):
    env: str = "production"


@lru_cache()
def get_settings():
    if(os.environ.get("ENV") == "development"):
        return DevSettings()
    elif(os.environ.get("ENV") == "test"):
        return TestSettings()
    elif(os.environ.get("ENV") == "production"):
        return ProdSettings()
    else:
        return DefaultSettings()
