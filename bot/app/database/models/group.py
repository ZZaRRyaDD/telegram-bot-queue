import zoneinfo

from sqlalchemy import Boolean, Column, String, orm

from .base import BaseTable

AVAILABLE_TIMEZONES = sorted([
    zone
    for zone in zoneinfo.available_timezones()
    if "Asia" in zone or "Europe" in zone
])


class Group(BaseTable):
    """Model for each group."""
    __tablename__ = "groups"

    name = Column(String(32), unique=True, nullable=False)
    secret_word = Column(String(128), nullable=False)
    random_queue = Column(Boolean, default=False)
    time_zone = Column(String(32), default="Asia/Krasnoyarsk", nullable=False)

    students = orm.relationship(
        "User",
        lazy="subquery",
        back_populates="group",
    )
    subjects = orm.relationship(
        "Subject",
        lazy="subquery",
        back_populates="group",
    )
