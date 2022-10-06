from sqlalchemy import BigInteger, Column, ForeignKey, Integer

from ..connect import Base


class Queue(Base):
    """Model for each queue."""
    __tablename__ = "queue"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    number = Column(Integer)

    def __str__(self) -> str:
        """Return representation of object in string."""
        return f"Queue of {self.subject_id} subject and {self.user_id} user"
