import asyncio
import datetime
import itertools
import random
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.utils.exceptions import BotBlocked

from app.database.models import Weekday
from app.database.repositories import (
    GroupRepository,
    QueueRepository,
    ScheduleRepository,
    SubjectRepository,
    UserRepository,
)
from app.enums import SubjectTypeEnum

from .services import is_even_week

SATURDAY = 5
DAYS_BEFORE_SUBJECT = 1


async def send_message_users(message: str, bot: Bot, reminder_time: datetime.time | None = None) -> None:
    """Function for send message for users with group."""
    current_time = datetime.datetime.now()
    
    schedules = await ScheduleRepository.get_schedule(can_select=True)
    if schedules:
        subjects = [
            asyncio.create_task(SubjectRepository.get_subject(schedule.subject_id))
            for schedule in schedules
        ]
        groups = {subject.group for subject in (await asyncio.gather(*subjects))}
        for group in groups:
            group_time = current_time.astimezone(tz=ZoneInfo(group.time_zone))
            if (
                reminder_time is None
                or (reminder_time.hour == group_time.hour and reminder_time.minute == group_time.minute)
            ):
                for student in group.students:
                    try:
                        await bot.send_message(
                            student.id,
                            message,
                        )
                    except BotBlocked:
                        pass


async def activate_after_tomorrow_subjects() -> None:
    """Function for activate next subjects."""
    after_tomorrow = datetime.date.today() + datetime.timedelta(
        days=DAYS_BEFORE_SUBJECT,
    )
    weekday = ""
    for item in Weekday:
        if item.value == after_tomorrow.weekday():
            weekday = item.name
            break
    
    if weekday != "":
        date_protection_schedule = await ScheduleRepository.get_schedule(
            date_protection=after_tomorrow,
        )
        date_number_schedule = await ScheduleRepository.get_schedule(
            date_number=weekday,
        )

        dates = set()
        for date in itertools.chain(date_protection_schedule, date_number_schedule):
            date_id = date.id
            if date_id not in dates:
                dates.add(date_id)
                await ScheduleRepository.change_status_subjects(True, schedule_id=date_id)

    await ScheduleRepository.change_status_subjects(
        False,
        week=is_even_week(after_tomorrow).constant,
    )


async def send_reminder(bot: Bot, reminder_time: datetime.time | None) -> None:
    """Send remind for stay in queue."""
    await send_message_users(
        "Не забудь записаться на сдачу лабораторной работы. В 8:00 будут результаты",
        bot,
        reminder_time,
    )


async def send_top(bot: Bot, top_time: datetime.time) -> None:
    """Send result queue."""
    current_time = datetime.datetime.now()

    await QueueRepository.cleaning_subject()
    schedule = await ScheduleRepository.get_schedule(can_select=True)
    subject_template = "Очередь по дисциплине '{0}'\n{1}"
    lab_template = "Лабораторная работа №{0}\n{1}\n\n"
    event_template = "{0} {1}\n{2}\n\n"
    if schedule:
        for subject_id in [item.subject_id for item in schedule]:
            subject = await SubjectRepository.get_subject(
                subject_id=subject_id,
                users_practice=True,
            )
            if not subject.users_practice:
                continue
            group = await GroupRepository.get_group(
                group_id=subject.group_id,
                students=True,
            )
            group_time = current_time.astimezone(tz=ZoneInfo(group.time_zone))
            if group_time.hour != top_time.hour or group_time.minute != top_time.minute:
                continue
            all_users = group.students
            list_labs = []
            for number in range(1, subject.count_practices + 1):
                params = {
                    "subject_id": subject.id,
                    "number_practice": number,
                }
                users = await QueueRepository.get_users_by_number(params)
                if users:
                    if group.random_queue:
                        random.shuffle(users)
                    list_queue = []
                    for index, user_id in enumerate(users):
                        user = await UserRepository.get_user(user_id)
                        list_queue.append(f"{index + 1}. {user.full_name}")
                    if subject.subject_type == SubjectTypeEnum.LABORATORY_WORK.value:
                        list_labs.append(
                            lab_template.format(number, "\n".join(list_queue))
                        )
                    else:
                        list_labs.append(
                            event_template.format(
                                subject.subject_type,
                                subject.name,
                                "\n".join(list_queue),
                            )
                        )
                for index, user in enumerate(users, 1):
                    params["number_in_list"] = index
                    params["user_id"] = user
                    await QueueRepository.update_queue_info(params)
            for student in all_users:
                try:
                    await bot.send_message(
                        student.id,
                        subject_template.format(
                            subject.name,
                            "".join(list_labs),
                        ),
                    )
                except BotBlocked:
                    pass
    await ScheduleRepository.change_status_subjects(False, can_select_to_change=True)
    await activate_after_tomorrow_subjects()
    await send_message_users(
        "Запись на следующие лабораторные работы доступна",
        bot,
    )
