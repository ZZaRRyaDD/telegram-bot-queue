import os
import random
from datetime import date, datetime, time, timedelta

from app.database.models import Subject, Group
from app.database.repositories import GroupActions, UserActions
from app.enums import SubjectPassesEnum, SubjectTypeEnum

DAY_WEEKS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]
DIFFERENCE_TIME_HOURS = 7


def get_time(str_time: str) -> str:
    """Get time in utc."""
    str_time_obj = time.fromisoformat(str_time)
    return (
        datetime.combine(date(2, 2, 2), str_time_obj) -
        timedelta(hours=DIFFERENCE_TIME_HOURS)
    ).time().isoformat("minutes")


async def check_admin(id: int) -> bool:
    """Check for admin user."""
    return id == int(os.getenv("ADMIN_ID"))


async def is_headman(id: int) -> bool:
    """Is user headman or not."""
    user = UserActions.get_user(id)
    if user:
        return user.is_headman
    return False


async def member_group(id: int) -> bool:
    """Check for member of some group."""
    user = UserActions.get_user(id)
    if user:
        return user.group_id is not None
    return False


async def polynomial_hash(string: str) -> int:
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


async def print_info(user_id: int) -> str:
    """Return info about user."""
    user = UserActions.get_user(user_id, group=True)
    info = f"ID: {user.id}\n"
    info += f"Фамилия Имя: {user.full_name}\n"
    group = (
        user.group.name
        if user.group is not None
        else ""
    )
    status = 'старостой' if user.is_headman else 'студентом'
    info += f"Вы являетесь {status} {group}\n"
    return info


async def get_schedule_name(item: dict) -> str:
    """Return info about day week and type of pass."""
    type_week = ""
    for week in SubjectPassesEnum:
        if week.value == item["week"]:
            type_week = week.description.lower()
    return f"{DAY_WEEKS[int(item['date_number'])]}, {type_week}"


async def get_info_schedule(subject: Subject) -> str:
    """Return info about schedule."""
    schedule = subject.days
    info = ""
    if not schedule:
        return "\t\tРасписание отсутствует\n"
    if subject.subject_type == SubjectTypeEnum.LABORATORY_WORK.value:
        even_week = list(filter(lambda x: x.week == SubjectPassesEnum.EACH_EVEN_WEEK.constant, schedule))
        odd_week = list(filter(lambda x: x.week == SubjectPassesEnum.EACH_ODD_WEEK.constant, schedule))
        every_week = list(filter(lambda x: x.week == SubjectPassesEnum.EACH_WEEK.constant, schedule))
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
    else:
        date_protection = schedule[0].date_protection
        month = str(date_protection.month)
        month = f"0{month}" if len(month) == 1 else month
        data = f"{date_protection.day}.{month}.{date_protection.year}"
        info += f"\t\t\t\tВремя проведения - {data}\n"

    can_select = False
    for day in subject.days:
        if day.can_select:
            can_select = True
            break
    info += (
        f"\t\t\t\tСейчас {'можно' if can_select else 'нельзя'} выбрать\n"
    )
    return info


async def get_info_subject(subject: Subject) -> str:
    """Return info about subject."""
    info = f"\t\t{subject.name}\n"
    if subject.subject_type == SubjectTypeEnum.LABORATORY_WORK.value:
        info += f"\t\tКоличество лабораторных работ: {subject.count_practices}\n"
    info += await get_info_schedule(subject)
    return info


async def get_info_group(group: Group) -> str:
    """Return info about group."""
    info = ""
    info += f"ID: {group.id}\n"
    info += f"Название: {group.name}\n"
    if group.subjects:
        info += "Предметы:\n"
        for subject in group.subjects:
            info += await get_info_subject(subject)
    if group.students:
        info += "Состав группы:\n"
        info += "".join(
            [
                f"\t\t{index + 1}. {user.full_name}\n"
                for index, user in enumerate(group.students)
            ]
        )
    return info


async def get_all_info() -> str:
    """Get info about groups, subjects."""
    info = ""
    groups = await GroupActions.get_groups(subjects=True, students=True)
    if groups:
        for group in groups:
            info += f"{await get_info_group(group)}\n"
        return info
    return "Ничего нет"
