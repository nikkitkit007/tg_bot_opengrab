from dotenv import load_dotenv
import logging.config
import os
from pydantic import BaseModel


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


class Settings(BaseModel):
    API_TOKEN: str = os.getenv('API_TOKEN')

    DB_HOST: str = os.getenv('DB_HOST')
    DB_PORT: int = int(os.getenv('DB_PORT', 5432))
    DB_DATABASE: str = os.getenv('DB_DATABASE')
    DB_NAME: str = os.getenv('DB_NAME')
    DB_USER: str = os.getenv('DB_USER')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD')

    DB_ECHO: bool = False

    MAIL_LOGIN: str = os.getenv('MAIL_LOGIN')
    MAIL_PASSWORD: str = os.getenv('MAIL_PASSWORD')
    SMTP_HOST: str = os.getenv('SMTP_HOST', 'smtp.mail.ru')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', 465))
    SMTP_DEBUG: bool = False

    OPENGRAB_URL: str = 'https://api.opengrab.ru/v10'


logger = logging.getLogger('info_logger')

settings = Settings()


DB_URL = f'{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}'
ASYNC_DB_URL = f'postgresql+asyncpg://{DB_URL}'
SYNC_DB_URL = f'postgresql://{DB_URL}'

WORK_SCHEMA = 'tg'
