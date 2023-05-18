from sqlalchemy import Column, Integer, String, Boolean
from db.connection import Base


class User(Base):
    __tablename__ = 'users'

    def __init__(self, mail=None, is_admin=None, is_auth=None, tg_id=None, role=None):
        self.mail = mail
        self.is_admin = is_admin
        self.is_auth = is_auth
        self.tg_id = tg_id
        self.role = role

    @property
    def dict(self):
        r = self.__dict__
        r.pop('_sa_instance_state', None)
        return r

    id = Column(Integer, primary_key=True)
    mail = Column(String)
    is_admin = Column(Boolean)
    is_auth = Column(Boolean)
    tg_id = Column(Integer)
    role = Column(String)
