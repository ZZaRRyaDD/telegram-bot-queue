from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, orm

from .connect import Base


class Queue(Base):
    """Model for each queue."""
    __tablename__ = "queue"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))


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
    )
    group = Column(Integer, ForeignKey("groups.id"), nullable=True)

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"User {self.full_name}, {self.group}"


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
    users = orm.relationship(
        "User",
        secondary="queue",
        back_populates="subjects",
    )
    days = orm.relationship("Date", back_populates="subjects")
    can_select = Column(Boolean, default=True)

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"Subject {self.name} for group {self.group}"


class Date(Base):
    """Model for each days."""
    __tablename__ = "days"

    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    subject = Column(Integer, ForeignKey("subjects.id"))
    subjects = orm.relationship("Subject", back_populates="days")

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"Date {self.number}"
