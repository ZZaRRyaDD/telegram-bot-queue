from sqlalchemy import Boolean, Column, ForeignKey, Integer

from ..connect import Base


class Schedule(Base):
    """Model for each subject."""
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    on_even_week = Column(Boolean, default=None)
    date_number = Column(Integer)
    subject_id = Column(Integer, ForeignKey("subjects.id"))

    def __str__(self) -> str:
        """Return representation of object in string."""
        return (
            f"Schedule for {self.subject_id} subject, "
            f"on date {self.date_number}"
        )
