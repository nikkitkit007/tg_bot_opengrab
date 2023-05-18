import logging
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import Settings
from tg_bot.states import MenuState, AuthState, AdminMenuState, SubscribeSettings, Newsletter

from tg_bot.utils import validate

from db.connection import async_session

from db.worker.user_wrk import UserWorker

settings = Settings()

logging.basicConfig(level=logging.WARNING)
logger = settings.logger

bot = Bot(token=settings.API_TOKEN)

dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


def is_auth(tg_id: int) -> bool:
    # async with async_session() as session:
    #     user = await UserWorker.get(session, tg_id)
    #     await session.commit()
    # if user.is_auth:
    #     return True
    # return False
    return True


def show_buttons():
    pass


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """
    1) проверка в базе, авторизирован ли пользователь
    """
    user_tg_id = message.from_user.id
    if is_auth(user_tg_id):
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
        data['email'] = message.text
        email = data['email']
        await message.reply(f"email: {email}")
        await state.finish()


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


# def ask_mail(message: types.Message, state: FSMContext):
#     context.user_data['mail'] = update.message.text
#     context.user_data['code'] = generate_code()
#     if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", context.user_data['mail']) or (
#             "@niuitmo.ru" not in context.user_data['mail'] and "@itmo.ru" not in context.user_data['mail']):
#         context.bot.sendMessage(chat_id=update.message.chat_id,
#                                 text='Почта не верна, попробуйте снова')
#         return State.ASK_MAIL
#     else:
#         send_code_email(context.user_data['mail'], context.user_data['code'])  # отправка кода
#         context.bot.sendMessage(chat_id=update.message.chat_id,
#                                 text='На почту: {} отправлен код. Введите его сообщением'.format(
#                                     context.user_data['mail']))
#         context.user_data['attempts'] = 0
#         return State.ASK_CODE
#
#
# def send_code_email(email, code):
#     smtp_obj = smtplib.SMTP_SSL('smtp.mail.ru', 465)
#     # smtpObj.debuglevel(True)
#     smtp_obj.login(mail_login, mail_password)
#     smtp_obj.sendmail(from_addr=mail_login, to_addrs=[email], msg='Printer code is: {}'.format(code))
#     smtp_obj.quit()


if __name__ == '__main__':
    logger.info("Start bot app...")
    executor.start_polling(dp, skip_updates=True)
