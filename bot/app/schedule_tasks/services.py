import calendar
import datetime

from app.enums import SubjectPassesEnum


def is_even_week(date: datetime.date) -> SubjectPassesEnum:
    """Return True if week is even, or False if odd."""
    day, month, year = date.day, date.month, date.year
    calendar_ = calendar.TextCalendar(calendar.MONDAY)
    lines = calendar_.formatmonth(year, month).split('\n')
    days_by_week = [week.lstrip().split() for week in lines[2:]]
    str_day = str(day)
    for index, week in enumerate(days_by_week):
        if str_day in week:
            if (index + 1) % 2 == 0:
                return SubjectPassesEnum.EACH_EVEN_WEEK
            return SubjectPassesEnum.EACH_ODD_WEEK
    return SubjectPassesEnum.EACH_WEEK
