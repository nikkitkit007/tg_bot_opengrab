import logging
import re

from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import Settings
from tg_bot.states import MenuState, AuthState, AdminMenuState, SubscribeSettings, Newsletter

from tg_bot.utils import validate, ask_mail, send_code_email

from db.connection import async_session
from db.worker.user_wrk import UserWorker, User

settings = Settings()

logging.basicConfig(level=logging.WARNING)
logger = settings.logger

bot = Bot(token=settings.API_TOKEN)

dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


async def is_auth(tg_id: int) -> bool:
    async with async_session() as session:
        user = await UserWorker.get(session, tg_id)
        if not user:
            user_data = User(tg_id=tg_id, is_admin=False, is_auth=True, role='Author')
            await UserWorker.add(session, user_data.dict)
            await session.commit()
            # запуск авторизации через почту #!todo
            return True
    if user[0].is_auth:
        return True
    return False


def show_buttons():
    pass


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """
    1) проверка в базе, авторизирован ли пользователь
    2) если не авторизирован, то выполняется авторизация через почту
    """
    user_tg_id = message.from_user.id
    if await is_auth(user_tg_id):
        await MenuState.main.set()
        await message.answer('Выберите действие:', reply_markup=MenuState.keyboard)
    else:
        await AuthState.waiting_for_email.set()
        await message.answer("Для авторизации необходимо ввести ваш <b>mail</b> с помощью которого вы регистрировались",
                             parse_mode='HTML')


@dp.message_handler(commands=['help'])
async def process_start_command(message: types.Message, state: FSMContext):
    await message.answer("Бот для работы с ...\n"
                         "Функционал:\n"
                         "\t-Просмотр информации о подписке\n"
                         "\t-Обновление времени рассылки\n"
                         )


@dp.message_handler(state=AuthState.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        email = message.text
        code = str(12345)
        data['email'] = email
        data['code'] = code
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
            await message.reply(f"Почта не верна, попробуйте снова")
            return AuthState.waiting_for_email.set()
        else:
            send_code_email(email, code)  # отправка кода
            await message.reply(f"На почту: {email} отправлено письмо с кодом подтверждения.\nВведите код из письма.")
            return AuthState.waiting_for_code.set()


@dp.message_handler(state=AuthState.waiting_for_code)
async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        code = data['code']

        if code == message.text:
            await message.answer("Авторизация выполнена успешно")
            await MenuState.main.set()
            await message.answer('Выберите действие:', reply_markup=MenuState.keyboard)
        else:
            pass


@dp.message_handler(state=MenuState.main)
async def main_menu(message: types.Message, state: FSMContext):
    if message.text == 'Рассылка':
        await Newsletter.main.set()
        await message.answer('Выберите действие:', reply_markup=Newsletter.keyboard)
    elif message.text == 'Подписка':
        await SubscribeSettings.main.set()
        await message.answer('Выберите действие:', reply_markup=SubscribeSettings.keyboard)
    else:
        await message.reply('Не верная команда.')


@dp.message_handler(state=SubscribeSettings.main)
async def subscribe_settings_menu(message: types.Message, state: FSMContext):
    if message.text == 'Информация о подписке':
        logger.info(message.text)
    elif message.text == 'Изменить время получения рассылки':
        logger.info(message.text)
    elif message.text == 'Изменить тариф':
        logger.info(message.text)
    elif message.text == 'Назад':
        await MenuState.main.set()
        await message.answer('Выберите действие:', reply_markup=MenuState.keyboard)
    else:
        await message.reply('Не верная команда.')


@dp.message_handler(state=Newsletter.main)
async def news_letter_menu(message: types.Message, state: FSMContext):
    if message.text == 'Получить сейчас рассылку в чат':
        logger.info(message.text)
    elif message.text == 'Получить сейчас рассылку в на почту':
        logger.info(message.text)
    elif message.text == 'Назад':
        await MenuState.main.set()
        await message.answer('Выберите действие:', reply_markup=MenuState.keyboard)
    else:
        await message.reply('Не верная команда.')


if __name__ == '__main__':
    logger.info("Start bot app...")
    executor.start_polling(dp, skip_updates=True)
