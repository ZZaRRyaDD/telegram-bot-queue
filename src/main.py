import os

from aiogram import Bot
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import Dispatcher

bot: Bot = Bot(token=os.getenv("TOKEN"))
dispatcher: Dispatcher = Dispatcher(bot, storage=RedisStorage2(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=5,
    pool_size=10,
))
