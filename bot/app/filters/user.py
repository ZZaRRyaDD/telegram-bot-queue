from typing import Union

from aiogram import types
from aiogram.dispatcher.filters import Filter

from app.database.repositories import UserRepository


class IsHeadman(Filter):
    async def check(self, message: Union[types.Message, types.CallbackQuery]):
        user = await UserRepository.get_user(message.from_user.id)
        return user.is_headman


class IsMemberOfGroup(Filter):
    def __init__(self, is_member: bool = True) -> None:
        self.is_member = is_member

    async def check(self, message: Union[types.Message, types.CallbackQuery]):
        user = await UserRepository.get_user(message.from_user.id)
        if self.is_member:
            return user.group_id is not None

        if not self.is_member:
            return user.group_id is None


class HasUser(Filter):
    async def check(self, message: Union[types.Message, types.CallbackQuery]):
        return await UserRepository.get_user(message.from_user.id)
