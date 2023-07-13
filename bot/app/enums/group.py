import enum


class GroupRandomQueueEnum(enum.Enum):
    """Class choices for type of random queue."""

    RANDOM_QUEUE = ("True", "Случайная генерация очереди")
    NOT_RANDOM_QUEUE = ("False", "Генерация в порядке записи")

    def __init__(self, value: str, description: str) -> None:
        self._value = value
        self.description = description
