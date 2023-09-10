import asyncio
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings


metadata = MetaData()
Base = declarative_base(metadata=metadata)

engine = create_async_engine(settings.DB_URL, echo=settings.DB_ECHO, future=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
