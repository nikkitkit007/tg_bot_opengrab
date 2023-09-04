from typing import List, Union
from functools import wraps

from aiogram import types

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests

from config import Settings
from tg_bot.schema import Roles

settings = Settings()
logger = settings.logger


async def set_user_tg(mail: str, tg_id: int):
    data = dict(tg_id=tg_id, email=mail)
    url = f"{settings.OPENGRAB_URL}/user"
    res = requests.put(url=url, json=data)
    logger.info(res.content)
    if res.status_code != 200:
        return False
    else:
        return True


async def get_user_role(user_tg_id: int) -> Union[str, None]:
    params = dict(tg_id=user_tg_id)
    url = f"{settings.OPENGRAB_URL}/user"
    res = requests.get(url=url, params=params)
    if res.status_code != 200:
        logger.info(res.content)
        return
    elif (res.status_code == 200 and res.json().get('result', [{}])[0].get('id')
          and res.json().get('result', [{}])[0].get('is')):
        return res.json()['result'][0]['is']
    else:
        logger.info(res.content)
        return


async def get_user_mail(user_tg_id: int):
    params = dict(tg_id=user_tg_id)
    url = f"{settings.OPENGRAB_URL}/user"
    res = requests.get(url=url, params=params)
    if res.status_code != 200:
        logger.info(res.content)
        return
    elif (res.status_code == 200 and res.json().get('result', [{}])[0].get('id')
          and res.json().get('result', [{}])[0].get('is')):
        return res.json()['result'][0]['name']
    else:
        logger.info(res.content)
        return


def send_email(email, subject, message):
    smtp_obj = smtplib.SMTP_SSL(Settings.SMTP_HOST, Settings.SMTP_PORT)
    smtp_obj.set_debuglevel(Settings.SMTP_DEBUG)
    smtp_obj.login(Settings.MAIL_LOGIN, Settings.MAIL_PASSWORD)

    msg = MIMEMultipart()
    msg['From'] = Settings.MAIL_LOGIN
    msg['To'] = email
    msg['Subject'] = subject
    message_text = message
    msg.attach(MIMEText(message_text, 'plain', 'utf-8'))

    smtp_obj.sendmail(from_addr=Settings.MAIL_LOGIN, to_addrs=[email], msg=msg.as_string())
    smtp_obj.quit()


def send_code_email(email, code):
    subject = 'Авторизация в ТГ боте'
    message = f'Ваш код для авторизации в OpenGrab-боте: {code}'
    send_email(email, subject, message)


def send_news_letter(email, news_letter):
    subject = 'Рассылка по вашему запросу'
    message = f'Рассылка по вашему запросу:\n{news_letter}'
    send_email(email, subject, message)


def is_mail_exist(email):
    # params = dict(email="jeff.ebrilo@gmail.com")
    # todo need 404 if user not found
    params = dict(email=email)
    url = f"{settings.OPENGRAB_URL}/user"
    res = requests.get(url=url, params=params)
    if res.status_code != 200:
        logger.info(res.content)
        return False
    elif res.status_code == 200 and res.json().get('result', [{}])[0].get('id') and res.json().get('result', [{}])[
        0].get('is'):
        return True
    else:
        logger.info(res.content)
        return False


def validate(white_role_list: List[Roles] = [], black_role_list: List[Roles] = []):
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
