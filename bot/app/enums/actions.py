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
    CANCEL = ("Cancel", "Отмена действия")


class EventActionsEnum(BaseActions):
    """Class choices of event actions."""

    CREATE = ("Create", "Добавить событие")
    UPDATE = ("Update", "Обновить событие")
    DELETE = ("Delete", "Удалить событие")
    CANCEL = ("Cancel", "Отмена действия")


class GroupActionsEnum(BaseActions):
    """Class choices of group actions."""

    CREATE = ("Create", "Создать группу")
    UPDATE = ("Update", "Обновить группу")
    DELETE = ("Delete", "Удалить группу")
    CANCEL = ("Cancel", "Отмена действия")


class ScheduleActionsEnum(BaseActions):
    """Class choices of schedule actions."""

    ADD = ("Add", "Добавить расписание")
    DELETE = ("Delete", "Удалить расписание")
    NEXT_ACTION = ("Next", "Продолжить изменение предмета")
    CANCEL = ("Cancel", "Отмена действия")


class UserRepositoryEnum(BaseActions):
    """Class choices of user actions."""

    UPDATE = ("Update", "Редактирование профиля")
    DELETE = ("Delete", "Удаление профиля")
    CANCEL = ("Cancel", "Отмена действия")
