import logging
from logging.config import dictConfig

from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates

from app.utils.logger import LogConfig
from config import get_settings

# Templating for google login example
templates = Jinja2Templates(directory="app/templates")

# Config settings
settings = get_settings()

# Settings for logging
dictConfig(LogConfig().dict())
logger = logging.getLogger("default_logger")
logger.info(f"Starting application on {settings.env} environment")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="authentications/login",
)
