from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
import asyncio

from tg_bot.utils import get_user_role, Roles
from config import Settings


settings = Settings()
logger = settings.logger


class AuthState(StatesGroup):
    start = State()
    waiting_for_email = State()
    waiting_for_code = State()


async def get_keyboard(user_tg_id: int, state):
    state.keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    role = await get_user_role(user_tg_id=user_tg_id)
    if role == Roles.author and state.base_buttons:
        state.keyboard.add(*state.base_buttons)
    elif role == Roles.admin:
        if state.admin_buttons:
            state.keyboard.add(*state.admin_buttons)
        if state.base_buttons:
            state.keyboard.add(*state.base_buttons)
    return state.keyboard


class MenuState(StatesGroup):
    main = State()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    base_buttons = ['Рассылка', 'Подписка']
    admin_buttons = ['Меню администратора']


class AdminMenuState(MenuState):
    main = State()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    base_buttons = ['Назад', ]
    admin_buttons = ['Управление клиентами', 'Системные настройки']

    keyboard.add(*base_buttons)


class AdminUserControlState(MenuState):
    main = State()
    user_info = State()
    statistics = State()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    base_buttons = ['Назад', ]
    admin_buttons = ['Получить информацию о пользователе', 'Получить статистику', ]

    keyboard.add(*admin_buttons)
    keyboard.add(*base_buttons)


class AdminSettingsState(MenuState):
    main = State()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    base_buttons = ['Назад', ]
    admin_buttons = ['Состояние почтового сервиса', 'Состояние бэкенда', ]

    keyboard.add(*admin_buttons)
    keyboard.add(*base_buttons)


class SubscribeSettings(StatesGroup):
    main = State()
    subscribe_info = State()
    update_subscribe_tariff = State()
    update_newsletter_time = State()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    base_buttons = ['Информация о подписке', 'Изменить время получения рассылки', 'Изменить тариф', 'Назад']
    keyboard.add(*base_buttons)


class Newsletter(StatesGroup):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    base_buttons = ['Получить сейчас рассылку в чат', 'Получить сейчас рассылку в на почту', 'Назад']
    keyboard.add(*base_buttons)

    main = State()

