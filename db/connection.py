import asyncio
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from config import Settings


metadata = MetaData()
Base = declarative_base(metadata=metadata)

engine = create_async_engine(Settings.DB_URL, echo=Settings.DB_ECHO, future=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
