from typing import Sequence

from sqlalchemy import select, insert, update, and_

from db.model import User
from db.connection import async_session as session


class UserWorker(User):

    @staticmethod
    async def add(user_data: dict):
        await session().execute(insert(User).values(user_data))

    @staticmethod
    async def get(tg_id: int = None, mail: str = None) -> Sequence[User]:
        query = select(User)
        if tg_id:
            query = query.where(and_(User.tg_id == tg_id))
        if mail:
            query = query.where(and_(User.mail == mail))

        return (await session().execute(query)).scalars().all()

    @staticmethod
    async def update(tg_id: int, mail: str = None, is_auth: bool = None):
        upd_data = {}
        if mail:
            upd_data['mail'] = mail
        if is_auth:
            upd_data['is_auth'] = is_auth
        query = update(User).where(User.tg_id == tg_id).values(upd_data)
        await session().execute(query)

    @staticmethod
    async def set_state(tg_id: int, state: str):
        upd_data = {state: state}
        query = update(User).where(User.tg_id == tg_id).values(upd_data)
        await session().execute(query)
