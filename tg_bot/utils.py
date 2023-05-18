import smtplib
from typing import NamedTuple, List
from functools import wraps

from aiogram import types

from db.connection import async_session
from db.worker.user_wrk import UserWorker

from config import Settings


class Roles(NamedTuple):
    author = 'author'
    admin = 'admin'


async def get_user_role(user_tg_id: int):
    async with async_session() as session:
        user = await UserWorker.get(session, user_tg_id)
        await session.commit()
    if user[0].is_auth:
        return user[0].role
    return


def send_code_email(email, code):
    smtp_obj = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    # smtpObj.debuglevel(True)
    smtp_obj.login(Settings.MAIL_LOGIN, Settings.MAIL_PASSWORD)
    smtp_obj.sendmail(from_addr=Settings.MAIL_LOGIN, to_addrs=[email], msg=f'Ваш код для авторизации в боте: {code}')
    smtp_obj.quit()


def validate(white_role_list: List[Roles] = None, black_role_list: List[Roles] = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(message: types.Message, *args, **kwargs):
            if message.from_user:
                tg_id = message.from_user.id
                role = await get_user_role(user_tg_id=tg_id)
                if role:
                    if role in white_role_list and role not in black_role_list:
                        return await func(message, *args, **kwargs)
                await message.answer("Вы не имеете прав для совершения этого действия")

            # Если пользователь не имеет правильных ролей, можно выполнить дополнительные действия
            # Например, отправить сообщение об ошибке или проигнорировать запрос

        return wrapper

    return decorator
