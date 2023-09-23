import asyncio
import logging
import re
from random import randint

from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import settings, logger
from tg_bot.states import (MenuState, AuthState, AdminMenuState, SubscribeSettings,
                           Newsletter, get_keyboard, AdminSettingsState, AdminUserControlState)

from tg_bot.utils.user import (validate, is_mail_exist, get_user_role, set_user_tg, get_user_mail, get_news_letter)
from tg_bot.utils.mail import send_code_email, send_news_letter_email
from tg_bot.schema import Roles

from db.worker.user_wrk import UserWorker

logging.basicConfig(level=logging.WARNING)

bot = Bot(token=settings.API_TOKEN)

dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


async def on_startapp(dp):
    # todo send message to admins
    logger.info('Bot is running...')


async def is_auth(tg_id: int) -> bool:
    a = await UserWorker.get(tg_id)
    print(a)

    if res := await get_user_role(user_tg_id=tg_id):
        return True
    return False


async def auth(message: types.Message):
    """
    1) проверка в базе, авторизирован ли пользователь
    2) если не авторизирован, то выполняется авторизация через почту
    """
    user_tg_id = message.from_user.id
    if await is_auth(user_tg_id):
        await MenuState.main.set()
        await message.answer(MenuState.text_main, reply_markup=(await get_keyboard(user_tg_id=message.from_user.id,
                                                                                   state=MenuState)))
    else:
        await AuthState.waiting_for_email.set()
        await message.answer("Для авторизации необходимо ввести ваш <b>mail</b> с помощью которого вы регистрировались",
                             parse_mode='HTML')


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await auth(message)


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_text(message: types.Message):
    await auth(message)


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
        code = str(randint(10000, 100000 - 1))
        data['email'] = email
        data['code'] = code
        # async with async_session() as session:
        #     await UserWorker.update(session, tg_id=message.from_user.id, mail=email)
        #     await session.commit()

        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email) or not await is_mail_exist(email):
            await message.reply(f"Почта не верна, попробуйте снова")
            return await AuthState.waiting_for_email.set()
        else:
            send_code_email(email, code)  # отправка кода
            await message.reply(f"На почту: {email} отправлено письмо с кодом подтверждения.\nВведите код из письма.")
            return await AuthState.waiting_for_code.set()


@dp.message_handler(state=AuthState.waiting_for_code)
async def mail_auth(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        code = data['code']

        if code == message.text:
            await set_user_tg(mail=data['email'], tg_id=message.from_user.id)
            await message.answer("Авторизация выполнена успешно")
            await MenuState.main.set()
            await message.answer(MenuState.text_main, reply_markup=(await get_keyboard(user_tg_id=message.from_user.id,
                                                                                       state=MenuState)))
        else:
            pass


@dp.message_handler(state=MenuState.main)
async def main_menu(message: types.Message, state: FSMContext):
    if message.text == Newsletter.name:
        await Newsletter.main.set()
        await message.answer(Newsletter.text_main, reply_markup=Newsletter.keyboard)
    elif message.text == SubscribeSettings.name:
        await SubscribeSettings.main.set()
        await message.answer(SubscribeSettings.text_main, reply_markup=SubscribeSettings.keyboard)
    elif message.text == AdminMenuState.name:
        await activate_admin_menu(message)
    else:
        await message.reply('Не верная команда.')


@dp.message_handler(state=SubscribeSettings.main)
async def subscribe_settings_menu(message: types.Message, state: FSMContext):
    if message.text == 'Информация о подписке':
        await message.answer(f'{await get_user_role(message.from_user.id)}')
    elif message.text == 'Изменить время получения рассылки':
        await message.reply('PUT api/subscribe/settings')
        logger.info(message.text)
    elif message.text == 'Изменить тариф':
        await message.reply('PUT api/subscribe/tariff')
        logger.info(message.text)
    elif message.text == 'Назад':
        await MenuState.main.set()
        await message.answer(MenuState.text_main, reply_markup=(await get_keyboard(user_tg_id=message.from_user.id,
                                                                                   state=MenuState)))
    else:
        await message.reply('Не верная команда.')


@dp.message_handler(state=Newsletter.main)
async def news_letter_menu(message: types.Message, state: FSMContext):
    if message.text == 'Получить сейчас рассылку в чат':
        if news_letter := await get_news_letter(message.from_user.id):
            if (count_data := len(news_letter)) > 10:
                await message.answer(f"Число записей: {count_data}")
                await message.answer(news_letter[:10])
                await message.answer("Для получения всех записей, выполните запрос на почту")
            elif count_data == 0:
                await message.answer("Эфиров за выбранный период не было")
            else:
                await message.answer(news_letter[:10])
        else:
            await message.answer('Сервис получения рассылки временно недоступен')
    elif message.text == 'Получить сейчас рассылку в на почту':
        if news_letter := await get_news_letter(message.from_user.id):
            user_mail = await get_user_mail(message.from_user.id)
            logger.info(f'Sent news_letter on mail: {user_mail}')
            send_news_letter_email(user_mail, news_letter)
        else:
            await message.answer('Сервис получения рассылки временно недоступен')
        logger.info(message.text)
    elif message.text == 'Назад':
        await MenuState.main.set()
        await message.answer(MenuState.text_main, reply_markup=(await get_keyboard(user_tg_id=message.from_user.id,
                                                                                   state=MenuState)))
    else:
        await message.reply('Не верная команда.')


@validate(white_role_list=[Roles.admin, Roles.client])
async def activate_admin_menu(message):
    await AdminMenuState.main.set()
    await message.answer(MenuState.text_main, reply_markup=(await get_keyboard(user_tg_id=message.from_user.id,
                                                                               state=AdminMenuState)))


@dp.message_handler(state=AdminMenuState.main)
async def admin_menu(message: types.Message, state: FSMContext):
    if message.text == AdminUserControlState.name:
        await AdminUserControlState.main.set()
        await message.answer(AdminUserControlState.text_main, reply_markup=AdminUserControlState.keyboard)
    elif message.text == AdminSettingsState.name:
        await AdminSettingsState.main.set()
        await message.answer(AdminSettingsState.text_main, reply_markup=AdminSettingsState.keyboard)
    elif message.text == 'Назад':
        await MenuState.main.set()
        await message.answer(MenuState.text_main, reply_markup=(await get_keyboard(user_tg_id=message.from_user.id,
                                                                                   state=MenuState)))
    else:
        await message.reply('Не верная команда.')


@dp.message_handler(state=AdminUserControlState.main)
async def admin_control(message: types.Message, state: FSMContext):
    if message.text == 'Получить информацию о пользователе':
        logger.info(message.text)
    elif message.text == 'Получить статистику':
        logger.info(message.text)
    elif message.text == 'Назад':
        await AdminMenuState.main.set()
        await message.answer(AdminMenuState.text_main, reply_markup=AdminMenuState.keyboard)
    else:
        await message.reply('Не верная команда.')


@dp.message_handler(state=AdminSettingsState.main)
async def admin_settings(message: types.Message, state: FSMContext):
    if message.text == 'Состояние почтового сервиса':
        logger.info(message.text)
    elif message.text == 'Состояние бэкенда':
        logger.info(message.text)
    elif message.text == 'Назад':
        await AdminMenuState.main.set()
        await message.answer(AdminMenuState.text_main, reply_markup=AdminMenuState.keyboard)
    else:
        await message.reply('Не верная команда.')


async def scheduler():
    logger.info('Start scheduler...')
    while True:
        """
        1) get users list
        2) if time: -> sent message
        """
        print('Run scheduler task...')
        await asyncio.sleep(60)


if __name__ == '__main__':
    logger.info("Start bot app...")
    executor.start_polling(dp, skip_updates=True)
