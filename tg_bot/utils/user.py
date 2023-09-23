from typing import List, Union
from functools import wraps

from aiogram import types


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


async def _get_user(user_tg_id: int = None, email: str = ''):
    if user_tg_id:
        params = dict(tg_id=user_tg_id)
    elif email:
        params = dict(email=email)
    else:
        raise ValueError("Not set args for request")

    url = f"{settings.OPENGRAB_URL}/user"
    res = requests.get(url=url, params=params)
    if res.status_code != 200:
        logger.info(res.content)
        return
    elif (res.status_code == 200 and res.json().get('result', [{}])[0].get('id')
          and res.json().get('result', [{}])[0]):
        return res.json()['result'][0]
    else:
        logger.info(res.content)
        return


async def get_user_role(user_tg_id: int) -> Union[str, None]:
    return (await _get_user(user_tg_id))['is']


async def get_user_mail(user_tg_id: int):
    return (await _get_user(user_tg_id))['name']


async def is_mail_exist(email):
    return (await _get_user(email=email))['is']


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
