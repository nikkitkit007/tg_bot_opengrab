# import asyncio
# from sqlalchemy import Column, Integer, String, Table, MetaData, insert
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import declarative_base, sessionmaker
# from config import Settings
#
#
# metadata = MetaData()
# Base = declarative_base(metadata=metadata)
#
# engine = create_async_engine(Settings.DB_URL, echo=True, future=True)
# async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
#
#
# class User(Base):
#     __tablename__ = 'user'
#
#     id = Column(Integer, primary_key=True)
#     username = Column(String)
#     first_name = Column(String)
#     last_name = Column(String)
#
#
# async def create_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
#
# # async def create_user():
# #     async with engine.begin() as conn:
# #         q = insert(User).values(username="N", first_name='FN', last_name="LN")
# #         await conn.e
# #
#
# async def insert_user(user_data: dict):
#     async with async_session() as session:
#         # user = User(**user_data)
#         # session.add(user)
#         # await session.commit()
#         await session.execute(insert(User).values(**user_data))
#         await session.commit()
#
# # await insert_user({'username': 'johndoe', 'first_name': 'John', 'last_name': 'Doe'})
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(create_tables())
#     loop.run_until_complete(insert_user({'username': 'johndoe', 'first_name': 'John', 'last_name': 'Doe'}))
import asyncio
from db.model import *
from db.connection import engine, Base


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_tables())
