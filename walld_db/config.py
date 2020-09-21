from os import getenv
from pathlib import Path
from walld_db.helpers import logger_factory

log = logger_factory('walld_config')

_PROJECT_DIR = Path(__file__).parents[1]
ENV_PATH = _PROJECT_DIR / '.env'

try:
    from dotenv import load_dotenv
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=str(ENV_PATH), override=False)
        log.info(f'Loaded vars from .env file {str(ENV_PATH)}')
except ImportError:
    pass


class Config:
    DB_HOST = getenv('DB_HOST', "localhost")
    DB_PORT = getenv("DB_PORT", "5432")
    DB_USER = getenv("DB_USER")


DB_HOST = getenv('DB_HOST', "localhost")
DB_PORT = getenv("DB_PORT", "5432")
DB_USER = getenv("DB_USER")

assert DB_USER

DB_PASSWORD = getenv("DB_PASSWORD")

assert DB_PASSWORD

DB_NAME = getenv("DB_NAME")

assert DB_NAME


