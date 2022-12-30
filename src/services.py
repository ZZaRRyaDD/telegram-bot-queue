import os
import random
from datetime import date, datetime, time, timedelta

from database import GroupActions, ScheduleActions, UserActions, models

DAY_WEEKS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]
DIFFERENCE_TIME_HOURS = 7


def get_time(str_time: str) -> str:
    """Get time in utc."""
    str_time_obj = time.fromisoformat(str_time)
    return (
        datetime.combine(date(1, 1, 1), str_time_obj) -
        timedelta(hours=DIFFERENCE_TIME_HOURS)
    ).time().isoformat("minutes")


def check_admin(id: int) -> bool:
    """Check for admin user."""
    return id == int(os.getenv("ADMIN_ID"))


def check_user(id: int) -> bool:
    """Check register user or not."""
    return UserActions.get_user(id) is not None


def is_headman(id: int) -> bool:
    """Is user headman or not."""
    user = UserActions.get_user(id)
    if user:
        return UserActions.get_user(id).is_headman


def member_group(id: int) -> bool:
    """Check for member of some group."""
    user = UserActions.get_user(id)
    if user:
        return UserActions.get_user(id).group is not None


def check_empty_headman(id: int) -> bool:
    """Check for empty headman."""
    return is_headman(id) and not member_group(id)


def check_headman_of_group(id: int) -> bool:
    """Check headman how owner of group."""
    return is_headman(id) and member_group(id)


def check_count_subject_group(id: int) -> bool:
    """Check for count of subjects."""
    group = GroupActions.get_group(
        UserActions.get_user(id).group,
        subjects=True,
    )
    if group:
        return bool(group.subjects if group else group)


def polynomial_hash(string: str) -> int:
    """Calculate polinomial hash."""
    second_prime_const = 2 ** 64 - 59
    first_prime_const = random.randint(0, second_prime_const)
    hash_code = 0
    for letter in enumerate(string):
        hash_code = (
            ord(letter[1]) *
            first_prime_const ** (len(string) - letter[0] - 1)
        )
    return hash_code % second_prime_const


def print_info(user_id: int) -> str:
    """Return info about user."""
    user = UserActions.get_user(user_id)
    info = f"ID: {user.id}\n"
    info += f"Фамилия Имя: {user.full_name}\n"
    group = (
        GroupActions.get_group(user.group).name
        if user.group is not None
        else ""
    )
    status = 'старостой' if user.is_headman else 'студентом'
    info += f"Вы являетесь {status} {group}\n"
    return info


def get_schedule_name(item: models.Schedule) -> str:
    """Return info about day week and type of pass."""
    type_week = (
        "по четным неделям"
        if item["on_even_week"] is True
        else "по нечетным неделям" if item["on_even_week"] is False
        else "каждую неделю"
    )
    return f"{DAY_WEEKS[int(item['date_number'])]}, {type_week}"


def get_info_schedule(subject_id: int) -> str:
    """Return info about schedule."""
    schedule = ScheduleActions.get_schedule(subject_id=subject_id)
    info = ""
    if not schedule:
        return "\t\tРасписание отсутствует\n"
    even_week = list(filter(lambda x: x.on_even_week is True, schedule))
    odd_week = list(filter(lambda x: x.on_even_week is False, schedule))
    every_week = list(filter(lambda x: x.on_even_week is None, schedule))
    info += "\t\tРасписание:\n"
    if even_week:
        days = " ".join(
            [
                f"{DAY_WEEKS[day.date_number]}"
                for day in sorted(even_week, key=lambda x: x.date_number)
            ]
        )
        info += f"\t\t\t\t{days} - По четным неделям\n"
    if odd_week:
        days = " ".join(
            [
                f"{DAY_WEEKS[day.date_number]}"
                for day in sorted(odd_week, key=lambda x: x.date_number)
            ]
        )
        info += f"\t\t\t\t{days} - По нечетным неделям\n"
    if every_week:
        days = " ".join(
            [
                f"{DAY_WEEKS[day.date_number]}"
                for day in sorted(every_week, key=lambda x: x.date_number)
            ]
        )
        info += f"\t\t\t\t{days} - Каждую неделю\n"
    can_select = ScheduleActions.get_schedule(
        subject_id=subject_id,
        can_select=True,
    )
    info += (
        f"\t\t\t\tСейчас {'можно' if can_select else 'нельзя'} выбрать\n"
    )
    return info


def get_info_subject(subject: models.Subject) -> str:
    """Return info about subject."""
    info = f"\t\t{subject.name}\n"
    info += f"\t\tКоличество лабораторных работ: {subject.count}\n"
    info += get_info_schedule(subject.id)
    return info


def get_info_group(group: models.Group) -> str:
    """Return info about group."""
    info = ""
    info += f"ID: {group.id}\n"
    info += f"Название: {group.name}\n"
    if group.subjects:
        info += "Предметы:\n"
        for subject in group.subjects:
            info += get_info_subject(subject)
    info += "Состав группы:\n"
    info += "".join(
        [
            f"\t\t{index + 1}. {user.full_name}\n"
            for index, user in enumerate(group.students)
        ]
    )
    return info


def get_all_info() -> str:
    """Get info about groups, subjects."""
    info = ""
    groups = GroupActions.get_groups(subjects=True, students=True)
    if groups:
        for group in groups:
            info += f"{get_info_group(group)}\n"
        return info
    return "Ничего нет"
