from typing import List, Union
from functools import wraps
import io
import csv

from aiogram import types

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import requests

from config import settings, logger
from tg_bot.schema import Roles


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


def convert_dict_to_csv(data: dict):
    csv_buffer = io.StringIO()
    csv_writer = csv.DictWriter(csv_buffer, fieldnames=data[0].keys())
    csv_writer.writeheader()
    csv_writer.writerows(data)
    return csv_buffer.getvalue()


def send_email(email, subject, message, csv_data=None):
    smtp_obj = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
    smtp_obj.set_debuglevel(settings.SMTP_DEBUG)
    smtp_obj.login(settings.MAIL_LOGIN, settings.MAIL_PASSWORD)

    msg = MIMEMultipart()
    msg['From'] = settings.MAIL_LOGIN
    msg['To'] = email
    msg['Subject'] = subject
    message_text = message
    msg.attach(MIMEText(message_text, 'plain', 'utf-8'))

    if csv_data:
        csv_attachment = MIMEApplication(csv_data.encode('utf-8'), _subtype='csv')
        csv_attachment.add_header('content-disposition', 'attachment', filename='NewsLetter.csv')
        msg.attach(csv_attachment)

    smtp_obj.sendmail(from_addr=settings.MAIL_LOGIN, to_addrs=[email], msg=msg.as_string())
    smtp_obj.quit()


def send_code_email(email, code):
    subject = 'Авторизация в ТГ боте'
    message = f'Ваш код для авторизации в OpenGrab-боте: {code}'
    send_email(email, subject, message)


def send_news_letter_email(email, news_letter):
    subject = 'Рассылка по вашему запросу'
    message = f'Рассылка по вашему запросу'
    send_email(email, subject, message, csv_data=convert_dict_to_csv(news_letter))


async def get_news_letter(tg_id: int) -> dict:
    """
    https://api.opengrab.ru/v10/results?tg_id=1302431850
    """
    # params = dict(tg_id=tg_id)
    params = dict(tg_id='1302431850')
    url = f"{settings.OPENGRAB_URL}/results"
    res = requests.get(url=url, params=params)
    if res and res.status_code == 200:
        return res.json()['result']['0']
    else:
        return {}


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
