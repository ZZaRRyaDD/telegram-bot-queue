import enum

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, orm

from .connect import Base


class Queue(Base):
    """Model for each queue."""
    __tablename__ = "queue"

    user_id = Column(ForeignKey("users.id"), primary_key=True)
    subject_id = Column(ForeignKey("subjects.id"), primary_key=True)
    users = orm.relationship("User", back_populates="subjects")
    subjects = orm.relationship("Subject", back_populates="users")


class User(Base):
    """Model for each user."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(128), nullable=False)
    email = Column(String(128))
    is_headman = Column(Boolean, default=False)
    subjects = orm.relationship("Queue", back_populates="users")
    group = Column(Integer, ForeignKey("groups.id"), nullable=True)

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"User {self.full_name}, {self.email}, {self.group}"


class Group(Base):
    """Model for each group."""
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    students = orm.relationship("User")
    subjects = orm.relationship("Subject")
    name = Column(String(32), unique=True, nullable=False)
    secret_word = Column(String(128), nullable=False)

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"Group {self.name}"


class Subject(Base):
    """Model for each subject."""
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    group = Column(Integer, ForeignKey("groups.id"), nullable=False)
    users = orm.relationship("Queue", back_populates="subjects")
    days = orm.relationship("Date")

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"Subject {self.name} for group {self.group}"


class DaysOfWeek(enum.Enum):
    """Class choices."""

    monday = 1
    tuesday = 2
    wednesday = 3
    thursday = 4
    friday = 5
    saturday = 6


class Date(Base):
    """Model for each days."""
    __tablename__ = "days"

    name = Column(Enum(DaysOfWeek), primary_key=True)
    subject = Column(Integer, ForeignKey("subjects.id"), nullable=False)

    def __str__(self) -> str:
        """Return representation of object in string."""
        return self.name
