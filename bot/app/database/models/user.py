from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    orm,
)

from app.database.connection import Base


class User(Base):
    """Model for each user."""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    full_name = Column(String(256), nullable=False)
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
