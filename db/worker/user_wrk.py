from sqlalchemy import select, insert, update, and_

from db.model.users import User


class UserWorker(User):

    @staticmethod
    async def add(local_session, user_data: dict):
        await local_session.execute(insert(User).values(user_data))

    @staticmethod
    async def get(local_session, tg_id: int = None, mail: str = None) -> list:
        query = select(User)
        if tg_id:
            query = query.where(and_(User.tg_id == tg_id))
        if mail:
            query = query.where(and_(User.mail == mail))

        return (await local_session.execute(query)).scalars().all()
