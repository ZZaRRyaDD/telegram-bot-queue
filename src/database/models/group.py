from sqlalchemy import Column, Integer, String, orm

from ..connect import Base


class Group(Base):
    """Model for each group."""
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True, nullable=False)
    secret_word = Column(String(128), nullable=False)
    students = orm.relationship("User", lazy="subquery")
    subjects = orm.relationship("Subject", lazy="subquery")
