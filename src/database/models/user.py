from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, orm

from ..connect import Base


class User(Base):
    """Model for each user."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(128), nullable=False)
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
    group = Column(Integer, ForeignKey("groups.id"), nullable=True)

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"User {self.full_name}, {self.group}"
