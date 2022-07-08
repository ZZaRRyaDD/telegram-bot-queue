from aiogram.utils import executor

from database import init_db
from handlers import (register_handlers_admin, register_handlers_client,
                      set_commands_client)
from main import dispatcher


async def on_startup(_):
    """Action on startup app."""
    init_db()
    await set_commands_client(dispatcher)


register_handlers_client(dispatcher)
register_handlers_admin(dispatcher)
executor.start_polling(
    dispatcher,
    skip_updates=True,
    on_startup=on_startup,
)
