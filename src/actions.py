import logging
import os

from aiogram.utils import executor

from database import init_db
from handlers import (register_handlers_admin, register_handlers_cancel_action,
                      register_handlers_client, set_commands_client)
from main import bot, dispatcher

# webhook settings
WEBHOOK_HOST = f'{os.getenv("WEBHOOK_HOST")}'
WEBHOOK_PATH = ''
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = os.getenv('WEBAPP_HOST')
WEBAPP_PORT = int(os.getenv('WEBAPP_PORT'))


async def on_startup(dispatcher) -> None:
    """Action on startup app."""
    init_db()
    await bot.set_webhook(WEBHOOK_URL)
    await set_commands_client(dispatcher)


async def on_shutdown(dispatcher) -> None:
    """Action on shutdown app."""
    await bot.delete_webhook()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


logging.basicConfig(filename="app.log")
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
register_handlers_cancel_action(dispatcher)
register_handlers_client(dispatcher)
register_handlers_admin(dispatcher)
executor.start_webhook(
    dispatcher=dispatcher,
    webhook_path=WEBHOOK_PATH,
    skip_updates=True,
    on_startup=on_startup,
    on_shutdown=on_shutdown,
    host=WEBAPP_HOST,
    port=WEBAPP_PORT,
)
