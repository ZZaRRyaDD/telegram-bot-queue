import enum


class AdminCommands(enum.Enum):
    """Class for admin commands."""

    SET_HEADMAN = ("set_headman", "Добавление/удаление старосты\n")
    ALL_INFO = ("all_info", "Вывод всей информации о всех группах\n")
    SEND_MESSAGE = ("send_message", "Отправка сообщений в моменте всем\n")
    COMMANDS = ("commands", "Вывод всех команд\n")

    def __init__(
        self,
        command: str,
        description: str,
    ) -> None:
        self.command = command
        self.description = description


class HeadmanCommands(enum.Enum):
    """Class for headman commands."""

    GROUP_INFO = ("group_info", "Информация о группе\n")
    EDIT_GROUP = ("edit_group", "Создание/обновление/удаление группы\n")
    EDIT_SUBJECT = ("edit_subject", "Создание/обновление/удаление предмета\n")

    def __init__(
        self,
        command: str,
        description: str,
    ) -> None:
        self.command = command
        self.description = description


class ClientCommands(enum.Enum):
    """Class for headman client."""

    START = ("start", "Создание аккаунта")
    INFO_PROFILE = ("info", "Информация о профиле")
    EDIT_PROFILE = ("edit_profile", "Обновление/удаление профиля")
    CHOICE_GROUP = ("select_group", "Изменить группу")
    STAY_QUEUE = ("stay_queue", "Встать/уйти из очереди")
    TO_ADMIN = ("to_admin", "Написать админу")
    PASS_PRACTICES = ("pass_practices", "Завершить практическую работу")

    def __init__(self, command: str, description: str) -> None:
        self.command = command
        self.description = description
