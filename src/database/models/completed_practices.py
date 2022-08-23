from sqlalchemy import Column, ForeignKey, Integer

from ..connect import Base


class CompletedPractices(Base):
    """Model for each completed practice."""
    __tablename__ = "completed_practices"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    number = Column(Integer)

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"Completed practice {self.subject_id} of user {self.user_id}"
