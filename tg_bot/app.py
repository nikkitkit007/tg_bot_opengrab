import logging
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy import insert
from config import Settings
from states import UserStates

from db.connection import async_session
from db.model.users import User

from db.worker.user_wrk import UserWorker


settings = Settings()

logging.basicConfig(level=logging.WARNING)

bot = Bot(token=settings.API_TOKEN)

dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    async with async_session() as session:
        users = await UserWorker.get(session)
        await session.commit()

    print([u.__dict__ for u in users])
    await message.reply("Привет! Как тебя зовут?")
    # await UserStates.waiting_for_email.set()


@dp.message_handler(commands=['help'])
async def process_start_command(message: types.Message, state: FSMContext):
    user_data = {
        "mail": 'test',
        "is_admin": False,
        "is_auth": True,
    }
    async with async_session() as session:
        await UserWorker.add(user_data, session)
        await session.commit()


@dp.message_handler(state=UserStates.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text
        email = data['email']
        await message.reply(f"email: {email}")
        await state.finish()


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
    logging.info("Start bot app...")
    executor.start_polling(dp, skip_updates=True)
