from aiogram.dispatcher.filters.state import State, StatesGroup


class AuthState(StatesGroup):
    start = State()
    waiting_for_email = State()
    waiting_for_code = State()


class MenuState(StatesGroup):
    main = State()


class AdminMenuState(MenuState):
    main = State()
    user_info = State()
    statistics = State()


class SubscribeSettings(StatesGroup):
    main = State()
    subscribe_info = State()
    update_subscribe_tariff = State()
    update_newsletter_time = State()


class Newsletter(StatesGroup):
    main = State()

