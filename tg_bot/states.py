from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types


class AuthState(StatesGroup):
    start = State()
    waiting_for_email = State()
    waiting_for_code = State()


class MenuState(StatesGroup):
    main = State()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    base_buttons = ['Рассылка', 'Подписка']
    admin_buttons = ['Управление клиентами', ]
    keyboard.add(*(base_buttons+admin_buttons))


class AdminMenuState(MenuState):
    main = State()
    user_info = State()
    statistics = State()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    base_buttons = ['Получить информацию о пользователе', 'Получить статистику', 'Назад']
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

