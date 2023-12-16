import asyncio

from config import logger, SCHEDULER_DELAY_TIME


async def scheduler():
    logger.info('Start scheduler...')
    while True:
        """
        1) get users list
        2) if time: -> sent message
        """
        logger.info('Doing scheduler task...')
        await asyncio.sleep(SCHEDULER_DELAY_TIME)
