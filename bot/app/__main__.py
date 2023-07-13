import asyncio
import logging
import os

import aioschedule
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

from app.handlers import (
    register_handlers_admin,
    register_handlers_cancel_action,
    register_handlers_client,
    set_commands_client,
)
from app.initialize import bot, dispatcher
from app.schedule_tasks import send_reminder, send_top
from app.services import get_time

DEBUG = os.getenv("DEBUG") != "False"
REMINDER_TIME = ("07:00:00", "12:00:00", "21:00:00")
SEND_TOP_TIME = "08:00:00"


async def scheduler():
    """Activate periodic tasks"""
    aioschedule.every().day.at(get_time(SEND_TOP_TIME)).do(send_top, bot=bot)
    for remide in REMINDER_TIME:
        aioschedule.every().day.at(get_time(remide)).do(send_reminder, bot=bot)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_) -> None:
    """Action on startup app."""
    await set_commands_client(dispatcher)
    if not DEBUG:
        await bot.set_webhook(
            f"{os.getenv('DOMAIN')}{os.getenv('WEBHOOK_PATH')}",
        )
        await bot.send_message(
            int(os.getenv("ADMIN_ID")),
            await bot.get_webhook_info(),
        )
    await bot.send_message(int(os.getenv("ADMIN_ID")), "Я запущен")
    asyncio.create_task(scheduler())


async def on_shutdown(_) -> None:
    """Action on shutdown app."""
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    await bot.send_message(int(os.getenv("ADMIN_ID")), "Я отрубаюсь")


logging.basicConfig(
    filename="app.log",
    format="%(asctime)s - %(levelname)s -%(message)s",
)
logging.getLogger('sqlalchemy.engine')
dispatcher.middleware.setup(LoggingMiddleware())
register_handlers_cancel_action(dispatcher)
register_handlers_client(dispatcher)
register_handlers_admin(dispatcher)


if __name__ == "__main__":
    if DEBUG:
        executor.start_polling(
            dispatcher=dispatcher,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
        )
    else:
        executor.start_webhook(
            dispatcher=dispatcher,
            webhook_path=os.getenv("WEBHOOK_PATH"),
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=os.getenv("WEBAPP_HOST"),
            port=int(os.getenv("WEBAPP_PORT")),
        )
