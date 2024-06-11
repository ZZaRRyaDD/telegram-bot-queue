from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    orm,
)

from .base import BaseTable


class User(BaseTable):
    """Model for each user."""
    __tablename__ = "users"

    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    surname = Column(String(128), nullable=False)
    is_headman = Column(Boolean, default=False)
    subjects_practice = orm.relationship(
        "Subject",
        secondary="queue",
        back_populates="users_practice",
        lazy="subquery",
    )
    subjects_completed = orm.relationship(
        "Subject",
        secondary="completed_practices",
        back_populates="users_completed",
        lazy="subquery",
    )

    group_id = Column(
        Integer,
        ForeignKey("groups.id", ondelete="SET NULL"),
        nullable=True,
    )
    group = orm.relationship(
        "Group",
        back_populates="students",
        lazy="joined",
    )
