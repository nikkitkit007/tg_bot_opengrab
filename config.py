from dotenv import load_dotenv
import logging.config
import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings

load_dotenv()

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default_formatter': {
            'format': '%(levelname)s : [%(asctime)s] %(funcName)s: %(message)s'
        }
    },

    'handlers': {
        'infoFileHandler': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'filename': 'logger.log',
            'formatter': 'default_formatter'
        },
        'errorFileHandler': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'filename': 'logger.log',
            'formatter': 'default_formatter'
        },
    },

    'loggers': {
        'info_logger': {
            'handlers': ['infoFileHandler'],
            'level': 'DEBUG',
            'propagate': True
        },
        'error_logger': {
            'handlers': ['errorFileHandler'],
            'level': 'ERROR',
            'propagate': True
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)


class Settings(BaseSettings):
    API_TOKEN: str = None

    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_DATABASE: str = 'postgres'
    DB_USER: str = 'postgres'
    DB_PASSWORD: str = 'mysecretpassword'

    DB_ECHO: bool = False

    MAIL_LOGIN: str = 'your_mail@mail.ru'
    MAIL_PASSWORD: str = 'your_smtp_password'
    SMTP_HOST: str = 'smtp.mail.ru'
    SMTP_PORT: int = 465
    SMTP_DEBUG: bool = False

    OPENGRAB_URL: str = 'https://api.opengrab.ru/v10'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


logger = logging.getLogger('info_logger')

settings = Settings()

DB_URL = f'{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}'
ASYNC_DB_URL = f'postgresql+asyncpg://{DB_URL}'
SYNC_DB_URL = f'postgresql://{DB_URL}'

WORK_SCHEMA = 'tg'

SCHEDULER_DELAY_TIME = 60  # seconds
