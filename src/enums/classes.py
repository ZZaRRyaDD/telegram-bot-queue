from dataclasses import dataclass


@dataclass
class SubjectCompact:
    """Class for send lab works in keyboard."""

    id: int
    name: str


@dataclass
class ScheduleCompact:
    """Class for send schedule in keyboard."""

    id: int
    name: str
