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

    SET_HEADMAN = ("set_headman", "Добавление/удаление старосты\n")
    ALL_INFO = ("all_info", "Вывод всей информации о всех группах\n")
    SEND_MESSAGE = ("send_message", "Отправка сообщений в моменте всем\n")
    DOWNLOAD_DATA = ("download_data", "Скачка данных в JSON\n")
    UPLOAD_DATA = ("upload_data", "Загрузка данных из JSON\n")
    COMMANDS = ("commands", "Вывод всех команд\n")


class HeadmanCommands(BaseCommands):
    """Class for headman commands."""

    GROUP_INFO = ("group_info", "Информация о группе\n")
    EDIT_GROUP = ("edit_group", "Создание/обновление/удаление группы\n")
    EDIT_SUBJECT = ("edit_subject", "Создание/обновление/удаление предмета\n")


class ClientCommands(BaseCommands):
    """Class for headman client."""

    START = ("start", "Создание аккаунта")
    INFO_PROFILE = ("info", "Информация о профиле")
    EDIT_PROFILE = ("edit_profile", "Обновление/удаление профиля")
    CHOICE_GROUP = ("select_group", "Изменить группу")
    STAY_QUEUE = ("stay_queue", "Встать/уйти из очереди")
    TO_ADMIN = ("to_admin", "Написать админу")
    PASS_PRACTICES = ("pass_practices", "Завершить практическую работу")


class OtherCommands(BaseCommands):
    """Class for other commands."""

    CANCEL = ("cancel", "Отмена действия")
