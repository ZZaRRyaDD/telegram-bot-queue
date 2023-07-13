from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.enums import (
    DaysOfWeekEnum,
    EventActionsEnum,
    GroupActionsEnum,
    GroupRandomQueueEnum,
    ScheduleActionsEnum,
    SubjectActionsEnum,
    SubjectPassesEnum,
    SubjectTypeEnum,
)

from .client import OtherCommands, get_list_keys


def select_days() -> InlineKeyboardMarkup:
    """Create keys for select days of week."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=DaysOfWeekEnum.MONDAY.weekday,
            callback_data=DaysOfWeekEnum.MONDAY.number,
        ),
        InlineKeyboardButton(
            text=DaysOfWeekEnum.TUESDAY.weekday,
            callback_data=DaysOfWeekEnum.TUESDAY.number,
        ),
    ).row(
        InlineKeyboardButton(
            text=DaysOfWeekEnum.WEDNESDAY.weekday,
            callback_data=DaysOfWeekEnum.WEDNESDAY.number,
        ),
        InlineKeyboardButton(
            text=DaysOfWeekEnum.THURSDAY.weekday,
            callback_data=DaysOfWeekEnum.THURSDAY.number,
        ),
    ).row(
        InlineKeyboardButton(
            text=DaysOfWeekEnum.FRIDAY.weekday,
            callback_data=DaysOfWeekEnum.FRIDAY.number,
        ),
        InlineKeyboardButton(
            text=DaysOfWeekEnum.SATURDAY.weekday,
            callback_data=DaysOfWeekEnum.SATURDAY.number,
        ),
    ).row(
        InlineKeyboardButton(
            text=DaysOfWeekEnum.STOP.weekday,
            callback_data=DaysOfWeekEnum.STOP.number,
        ),
    )
    return keyboard


def subject_action() -> InlineKeyboardMarkup:
    """Create keyboard for create/update/delete subject."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=SubjectActionsEnum.CREATE.description,
            callback_data=SubjectActionsEnum.CREATE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=SubjectActionsEnum.UPDATE.description,
            callback_data=SubjectActionsEnum.UPDATE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=SubjectActionsEnum.DELETE.description,
            callback_data=SubjectActionsEnum.DELETE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=SubjectActionsEnum.CANCEL.description,
            callback_data=SubjectActionsEnum.CANCEL.action,
        ),
    )
    return keyboard


def choice_schedule(schedule: list) -> InlineKeyboardMarkup:
    """Create keyboard for choice schedule."""
    keyboard = get_list_keys(schedule)
    keyboard.row(
        InlineKeyboardButton(
            text=OtherCommands.CANCEL.description,
            callback_data=OtherCommands.CANCEL.command,
        ),
    )
    return keyboard


def group_action() -> InlineKeyboardMarkup:
    """Create keyboard for create/update/delete group."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=GroupActionsEnum.CREATE.description,
            callback_data=GroupActionsEnum.CREATE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=GroupActionsEnum.UPDATE.description,
            callback_data=GroupActionsEnum.UPDATE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=GroupActionsEnum.DELETE.description,
            callback_data=GroupActionsEnum.DELETE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=GroupActionsEnum.CANCEL.description,
            callback_data=GroupActionsEnum.CANCEL.action,
        ),
    )
    return keyboard


def schedule_action() -> InlineKeyboardMarkup:
    """Create keyboard for schedule of subject."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=ScheduleActionsEnum.ADD.description,
            callback_data=ScheduleActionsEnum.ADD.action,
        ),
        InlineKeyboardButton(
            text=ScheduleActionsEnum.DELETE.description,
            callback_data=ScheduleActionsEnum.DELETE.action,
        )
    )
    keyboard.row(
            InlineKeyboardButton(
                text=ScheduleActionsEnum.NEXT_ACTION.description,
                callback_data=ScheduleActionsEnum.NEXT_ACTION.action,
            ),
        )
    keyboard.row(
        InlineKeyboardButton(
            text=ScheduleActionsEnum.CANCEL.description,
            callback_data=ScheduleActionsEnum.CANCEL.action,
        ),
    )
    return keyboard


def select_subject_passes() -> InlineKeyboardMarkup:
    """Create keyboard for select when subject passes."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=SubjectPassesEnum.EACH_WEEK.description,
            callback_data=SubjectPassesEnum.EACH_WEEK.bool_value,
        ),
    ).row(
        InlineKeyboardButton(
            text=SubjectPassesEnum.EACH_ODD_WEEK.description,
            callback_data=SubjectPassesEnum.EACH_ODD_WEEK.bool_value,
        ),
    ).row(
        InlineKeyboardButton(
            text=SubjectPassesEnum.EACH_EVEN_WEEK.description,
            callback_data=SubjectPassesEnum.EACH_EVEN_WEEK.bool_value,
        ),
    )
    return keyboard


def event_action() -> InlineKeyboardMarkup:
    """Create keyboard for create/update/delete event."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=EventActionsEnum.CREATE.description,
            callback_data=EventActionsEnum.CREATE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=EventActionsEnum.UPDATE.description,
            callback_data=EventActionsEnum.UPDATE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=EventActionsEnum.DELETE.description,
            callback_data=EventActionsEnum.DELETE.action,
        ),
    ).row(
        InlineKeyboardButton(
            text=EventActionsEnum.CANCEL.description,
            callback_data=EventActionsEnum.CANCEL.action,
        ),
    )
    return keyboard


def select_subject_type() -> InlineKeyboardMarkup:
    """Create keyboard for select types of subject."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=SubjectTypeEnum.COURSE_WORK.description,
            callback_data=SubjectTypeEnum.COURSE_WORK.type,
        ),
    ).row(
        InlineKeyboardButton(
            text=SubjectTypeEnum.SUMMER_PRACTICE.description,
            callback_data=SubjectTypeEnum.SUMMER_PRACTICE.type,
        ),
    ).row(
        InlineKeyboardButton(
            text=SubjectTypeEnum.GRADUATE_WORK.description,
            callback_data=SubjectTypeEnum.GRADUATE_WORK.type,
        ),
    )
    return keyboard


def select_random_queue_group() -> InlineKeyboardMarkup:
    """Create keyboard for select type of get queue of group."""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        InlineKeyboardButton(
            text=GroupRandomQueueEnum.RANDOM_QUEUE.description,
            callback_data=GroupRandomQueueEnum.RANDOM_QUEUE._value,
        ),
    ).row(
        InlineKeyboardButton(
            text=GroupRandomQueueEnum.NOT_RANDOM_QUEUE.description,
            callback_data=GroupRandomQueueEnum.NOT_RANDOM_QUEUE._value,
        ),
    )
    return keyboard
