import calendar
import datetime


def is_event_week(date: datetime.date) -> bool:
    """Return True if week is even, or False if odd."""
    day, month, year = date.day, date.month, date.year
    calendar_ = calendar.TextCalendar(calendar.MONDAY)
    lines = calendar_.formatmonth(year, month).split('\n')
    days_by_week = [week.lstrip().split() for week in lines[2:]]
    str_day = str(day)
    for index, week in enumerate(days_by_week):
        if str_day in week:
            return (index + 1) % 2 == 0
