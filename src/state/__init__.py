from .complete_practice import register_handlers_complete_practice
from .edit_account import register_handlers_change_account
from .edit_group import register_handlers_group
from .edit_subjects import register_handlers_subject
from .select_group import register_handlers_select_group
from .send_message import register_handlers_message
from .set_headman import register_handlers_set_headman
from .stay_queue import register_handlers_stay_queue

__all__ = (
    register_handlers_complete_practice,
    register_handlers_change_account,
    register_handlers_group,
    register_handlers_subject,
    register_handlers_select_group,
    register_handlers_message,
    register_handlers_set_headman,
    register_handlers_stay_queue,
)
