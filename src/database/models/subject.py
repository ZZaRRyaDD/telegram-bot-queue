from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, orm

from ..connect import Base


class Subject(Base):
    """Model for each subject."""
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    group = Column(Integer, ForeignKey("groups.id"), nullable=False)
    users_practice = orm.relationship(
        "User",
        secondary="queue",
        back_populates="subjects_practice",
        lazy="subquery",
    )
    on_even_week = Column(Boolean, default=None)
    days = orm.relationship(
        "Schedule",
        lazy="subquery",
    )
    users_completed = orm.relationship(
        "User",
        secondary="completed_practices",
        back_populates="subjects_completed",
        lazy="subquery",
    )
    count = Column(Integer)
    can_select = Column(Boolean, default=False)

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"Subject {self.name} for group {self.group}"
