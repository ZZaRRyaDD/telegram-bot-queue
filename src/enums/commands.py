import enum


class BaseCommands(enum.Enum):
    """Base class for create enum with commands."""

    def __init__(
        self,
        command: str,
        description: str,
    ) -> None:
        self.command = command
        self.description = description


class AdminCommands(BaseCommands):
    """Class for admin commands."""

    SET_HEADMAN = (
        "set_headman",
        "Добавление/удаление старосты\n",
    )
    ALL_INFO = (
        "all_info",
        "Вывод всей информации о всех группах\n",
    )
    SEND_MESSAGE = (
        "send_message",
        "Отправка сообщений в моменте всем\n",
    )
    COMMANDS = (
        "commands",
        "Вывод всех команд\n",
    )


class HeadmanCommands(BaseCommands):
    """Class for headman commands."""

    INFO_GROUP = (
        "info_group",
        "Просмотр информации о группе\n",
    )
    EDIT_GROUP = (
        "edit_group",
        "Создание/обновление/удаление/просмотр группы\n",
    )
    EDIT_SUBJECT = (
        "edit_subject",
        "Создание/обновление/удаление/просмотр предмета\n",
    )


class ClientCommands(BaseCommands):
    """Class for headman client."""

    START = (
        "start",
        "Создание аккаунта",
    )
    INFO_PROFILE = (
        "info_profile",
        "ПРосмотр информации о профиле",
    )
    EDIT_PROFILE = (
        "edit_profile",
        "Обновление/удаление профиля",
    )
    STAY_QUEUE = (
        "stay_queue",
        "Встать/уйти из очереди",
    )
    PASS_PRACTICES = (
        "pass_practices",
        "Завершить практическую работу",
    )
    CHOICE_GROUP = (
        "select_group",
        "Изменить группу",
    )
    TO_ADMIN = (
        "to_admin",
        "Написать админу",
    )


class OtherCommands(BaseCommands):
    """Class for other commands."""

    CANCEL = (
        "Cancel",
        "Отмена действия",
    )
