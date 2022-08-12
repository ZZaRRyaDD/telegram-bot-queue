from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, orm

from ..connect import Base


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
    can_select = Column(Boolean, default=False)
    count = Column(Integer)

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"Subject {self.name} for group {self.group}"