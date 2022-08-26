import logging
import os

from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

from database import init_db
from handlers import (
    register_handlers_admin,
    register_handlers_cancel_action,
    register_handlers_client,
    set_commands_client,
)
from main import bot, dispatcher

DEBUG = os.getenv("DEBUG", True)


async def on_startup(dispatcher) -> None:
    """Action on startup app."""
    init_db()
    await set_commands_client(dispatcher)
    if not DEBUG:
        await bot.set_webhook(os.getenv("WEBHOOK_URL"))
    await bot.send_message(int(os.getenv("ADMIN_ID")), "Я запущен")


async def on_shutdown(dispatcher) -> None:
    """Action on shutdown app."""
    if not DEBUG:
        await bot.delete_webhook()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    await bot.send_message(int(os.getenv("ADMIN_ID")), "Я отрубаюсь")


logging.basicConfig(
    filename="app.log",
    format="%(asctime)s - %(levelname)s -%(message)s",
)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
dispatcher.middleware.setup(LoggingMiddleware())
register_handlers_cancel_action(dispatcher)
register_handlers_client(dispatcher)
register_handlers_admin(dispatcher)

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
