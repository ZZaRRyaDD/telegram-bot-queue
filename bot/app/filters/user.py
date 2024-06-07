from typing import Union

from aiogram import types
from aiogram.dispatcher.filters import Filter

from app.database.repositories import UserActions


class IsHeadman(Filter):
    async def check(self, message: Union[types.Message, types.CallbackQuery]):
        user = await UserActions.get_user(message.from_user.id)
        if not user.is_headman:
            await message.answer("Вы не являетесь старостой")
        return user.is_headman


class IsMemberOfGroup(Filter):
    def __init__(self, is_member: bool = True) -> None:
        self.is_member = is_member

    async def check(self, message: Union[types.Message, types.CallbackQuery]):
        user = await UserActions.get_user(message.from_user.id)
        if self.is_member:
            if user.group_id is None:
                await message.answer("Вы не состоите в группе")
                return False
        else:
            if user.group_id is not None:
                await message.answer("Вы состоите в группе")
                return False
        return user.group_id is not None


class HasUser(Filter):
    async def check(self, message: Union[types.Message, types.CallbackQuery]):
        user = await UserActions.get_user(message.from_user.id)
        if not user:
            await message.answer("У вас отсутствует аккаунт в боте")
        return user
