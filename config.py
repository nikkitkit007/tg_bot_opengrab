from dotenv import load_dotenv
import logging.config
import os

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


class Settings:
    API_TOKEN = os.getenv('API_TOKEN')

    DB_HOST = os.getenv('POSTGRES_HOST')
    DB_PORT = os.getenv('POSTGRES_PORT')
    DB_NAME = os.getenv('POSTGRES_NAME')
    DB_USER = os.getenv('POSTGRES_USER')
    DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')

    DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    DB_ECHO = False

    logger = logging.getLogger('info_logger')
