from sqlalchemy import Column, ForeignKey, Integer

from ..connect import Base


class Date(Base):
    """Model for each days."""
    __tablename__ = "days"

    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    subject = Column(Integer, ForeignKey("subjects.id"))

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"Date {self.number}"
