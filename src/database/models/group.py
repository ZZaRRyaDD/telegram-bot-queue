from sqlalchemy import Column, Integer, String, orm

from ..connect import Base


class Group(Base):
    """Model for each group."""
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    students = orm.relationship("User", lazy="subquery")
    subjects = orm.relationship("Subject", lazy="subquery")
    name = Column(String(32), unique=True, nullable=False)
    secret_word = Column(String(128), nullable=False)

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"Group {self.name}"
