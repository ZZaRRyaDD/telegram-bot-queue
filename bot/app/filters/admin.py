from typing import Union

from aiogram import types
from aiogram.dispatcher.filters import Filter

from app.services import check_admin


class IsAdmin(Filter):
    async def check(self, message: Union[types.Message, types.CallbackQuery]):
        return await check_admin(message.from_user.id)
