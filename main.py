from aiogram.utils import executor
from tg_bot.app import dp
from config import settings, logger


if __name__ == '__main__':
    logger.info(settings.model_dump())
    executor.start_polling(dp, skip_updates=True)
