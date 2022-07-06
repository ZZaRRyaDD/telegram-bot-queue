import os

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from database import init_db


async def on_startup(_):
    """Action on startup app."""
    init_db()


def main():
    """Entrypoint for all app."""
    bot = Bot(token=os.getenv("TOKEN"))
    dispatcher = Dispatcher(bot)
    executor.start_polling(
        dispatcher,
        skip_updates=True,
        on_startup=on_startup,
    )


if __name__ == "__main__":
    main()
