import asyncio
from db.model import *
from db.connection import engine, Base


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_tables())
