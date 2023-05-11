from sqlalchemy import Column, Integer, String, Boolean
from db.connection import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    mail = Column(String)
    is_admin = Column(Boolean)
    is_auth = Column(Boolean)
