from typing import Optional

from sqlalchemy import delete, desc, orm, select, update

from .. import connect
from ..models import Subject


class SubjectActions:
    """Class with actions with subject."""

    @staticmethod
    def get_subject(
        subject_id: Optional[int] = None,
        users_practice: bool = False,
        last: bool = False,
    ) -> Optional[Subject]:
        """Get subject."""
        query = select(Subject)
        if subject_id is not None:
            query = query.where(Subject.id == subject_id)
        if users_practice:
            query = query.options(
                orm.subqueryload(Subject.users_practice),
            )
        if last:
            query = query.order_by(desc(Subject.id))
        with connect.SessionLocal() as session:
            subject = session.execute(query).first()
            return subject[0] if subject else None

    @staticmethod
    def get_subjects(
        users_practice: bool = False,
    ) -> Optional[list[Subject]]:
        """Get all subjects."""
        query = select(Subject)
        if users_practice:
            query = query.options(
                orm.subqueryload(Subject.users_practice),
            )
        with connect.SessionLocal() as session:
            subjects = session.execute(query).all()
            return [subject[0] for subject in subjects] if subjects else None

    @staticmethod
    def create_subject(subject: dict) -> Subject:
        """Create subject."""
        with connect.SessionLocal.begin() as session:
            session.add(Subject(**subject))
            session.commit()
        return SubjectActions.get_subject(last=True)

    @staticmethod
    def update_subject(subject_id: int, subject: dict) -> None:
        """Update subject."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                update(Subject).where(
                    Subject.id == subject_id,
                ).values(subject),
            )

    @staticmethod
    def delete_subject(id: int) -> None:
        """Delete subject by id."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(Subject).where(
                    Subject.id == id
                )
            )
