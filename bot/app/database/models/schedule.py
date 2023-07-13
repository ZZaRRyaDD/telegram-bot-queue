from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, orm

from ..connect import Base


class Schedule(Base):
    """Model for each subject."""
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    on_even_week = Column(Boolean, default=None)
    date_number = Column(Integer, default=None)
    subject_id = Column(
        Integer,
        ForeignKey("subjects.id", ondelete="CASCADE"),
    )
    can_select = Column(Boolean, default=False)
    date_protection = Column(Date, default=None)
    subject = orm.relationship(
        "Subject",
        lazy="joined",
        back_populates="days",
    )
