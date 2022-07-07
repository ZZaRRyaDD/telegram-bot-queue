import os

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from database import init_db
from handlers import client


async def on_startup(_):
    """Action on startup app."""
    init_db()


bot: Bot = Bot(token=os.getenv("TOKEN"))
dispatcher: Dispatcher = Dispatcher(bot)
client.register_handlers_client(dispatcher)
executor.start_polling(
    dispatcher,
    skip_updates=True,
    on_startup=on_startup,
)
