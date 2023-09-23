import asyncio
from aiogram.utils import executor
from tg_bot.app import dp, scheduler
from config import settings, logger


if __name__ == '__main__':
    logger.info(settings.model_dump())
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())
    executor.start_polling(dp, skip_updates=True)
