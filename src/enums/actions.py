import enum


class BaseActions(enum.Enum):
    """Base class for create enum with commands."""

    def __init__(self, action: str, description: str) -> None:
        self.action = action
        self.description = description


class SubjectActionsEnum(BaseActions):
    """Class choices of subject actions."""

    CREATE = ("Create", "Добавить предмет")
    UPDATE = ("Update", "Обновить предмет")
    DELETE = ("Delete", "Удалить предмет")


class GroupActionsEnum(BaseActions):
    """Class choices of group actions."""

    CREATE = ("Create", "Создать группу")
    UPDATE = ("Update", "Обновить группу")
    DELETE = ("Delete", "Удалить группу")


class ScheduleActionsEnum(BaseActions):
    """Class choices of schedule actions."""

    ADD = ("Add", "Добавить расписание")
    DELETE = ("Delete", "Удалить расписание")
    NEXT_ACTION = ("Next", "Продолжить создание предмета")


class UserActionsEnum(BaseActions):
    """Class choices of user actions."""

    UPDATE = ("Update", "Редактирование профиля")
    DELETE = ("Delete", "Удаление профиля")
