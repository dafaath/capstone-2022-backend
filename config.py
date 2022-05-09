from pydantic import BaseSettings
from functools import lru_cache


class DefaultSettings(BaseSettings):
    env: str = "development"
    db_user: str = "postgres"
    db_pass: str = ""
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "emodiary"


@lru_cache()
def get_settings():
    return DefaultSettings()
