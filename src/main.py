import os
import ssl

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

bot: Bot = Bot(token=os.getenv("TOKEN"))
dispatcher: Dispatcher = Dispatcher(bot, storage=MemoryStorage())
