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


class DevSettings(DefaultSettings):
    pass


class TestSettings(DefaultSettings):
    env: str = "test"


class ProdSettings(DefaultSettings):
    env: str = "production"


@lru_cache()
def get_settings():
    if(os.environ.get("env") == "development"):
        return DevSettings()
    elif(os.environ.get("env") == "test"):
        return TestSettings()
    elif(os.environ.get("env") == "production"):
        return ProdSettings()
    else:
        return DefaultSettings()
