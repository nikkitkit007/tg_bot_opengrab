from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base


metadata = MetaData()
Base = declarative_base(metadata=metadata)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer)
    mail = Column(String)
    is_auth = Column(Boolean)
    role = Column(String)
    state = Column(String)
