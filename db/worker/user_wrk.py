from sqlalchemy import select, insert, update, and_

from db.model.users import User


class UserWorker(User):

    @staticmethod
    async def add(user_data: dict, local_session):
        await local_session.execute(insert(User).values(user_data))

    @staticmethod
    async def get(local_session) -> list:
        query = select(User)

        return (await local_session.execute(query)).scalars().all()
