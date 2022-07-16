from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, orm

from .connect import Base


class Queue(Base):
    """Model for each queue."""
    __tablename__ = "queue"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    number = Column(Integer)


class User(Base):
    """Model for each user."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(128), nullable=False)
    is_headman = Column(Boolean, default=False)
    subjects = orm.relationship(
        "Subject",
        secondary="queue",
        back_populates="users",
        lazy="subquery",
    )
    group = Column(Integer, ForeignKey("groups.id"), nullable=True)

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"User {self.full_name}, {self.group}"


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


class Subject(Base):
    """Model for each subject."""
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    group = Column(Integer, ForeignKey("groups.id"), nullable=False)
    users = orm.relationship(
        "User",
        secondary="queue",
        back_populates="subjects",
        lazy="subquery",
    )
    days = orm.relationship("Date", lazy="subquery", innerjoin=True)
    can_select = Column(Boolean, default=True)
    count = Column(Integer)

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"Subject {self.name} for group {self.group}"


class Date(Base):
    """Model for each days."""
    __tablename__ = "days"

    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    subject = Column(Integer, ForeignKey("subjects.id"))

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"Date {self.number}"
