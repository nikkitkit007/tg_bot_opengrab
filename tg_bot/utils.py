import smtplib
from typing import NamedTuple, List
from functools import wraps

from aiogram import types

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from db.connection import async_session
from db.worker.user_wrk import UserWorker

from config import Settings


settings = Settings()
logger = settings.logger


class Roles(NamedTuple):
    author = 'author'
    admin = 'admin'


async def get_user_role(user_tg_id: int):
    async with async_session() as session:
        user = await UserWorker.get(session, user_tg_id)
        if user:
            if user[0].is_auth:
                return user[0].role
    return


def send_code_email(email, code):
    smtp_obj = smtplib.SMTP_SSL(Settings.SMTP_HOST, Settings.SMTP_PORT)
    # smtpObj.debuglevel(True)
    smtp_obj.login(Settings.MAIL_LOGIN, Settings.MAIL_PASSWORD)
    smtp_obj.sendmail(from_addr=Settings.MAIL_LOGIN, to_addrs=[email],
                      msg=MIMEText(f'Ваш код для авторизации в боте: {code}', 'plain', 'utf-8').as_string())
    smtp_obj.quit()


def validate(white_role_list: List[Roles] = None, black_role_list: List[Roles] = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(message: types.Message, *args, **kwargs):
            if message.from_user:
                tg_id = message.from_user.id
                role = await get_user_role(user_tg_id=tg_id)
                logger.info(f"user role: {role}")

                if role:
                    if role in white_role_list and role not in black_role_list:
                        return await func(message, *args, **kwargs)
                await message.answer("Вы не имеете прав для совершения этого действия")

        return wrapper

    return decorator
