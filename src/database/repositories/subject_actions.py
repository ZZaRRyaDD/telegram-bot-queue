from typing import Optional, Union

from sqlalchemy import delete, desc, orm, select, update

from .. import connect
from ..models import Subject


class SubjectActions:
    """Class with actions with subject."""

    @staticmethod
    def get_subject(
        id: Optional[int] = None,
        users: bool = False,
        last: bool = False,
    ) -> Optional[Subject]:
        """Get subject."""
        query = select(Subject)
        if id:
            query = query.where(Subject.id == id)
        if users:
            query = query.options(orm.subqueryload(Subject.users))
        if last:
            query = query.order_by(desc(Subject.id))
        with connect.SessionLocal() as session:
            subject = session.execute(query).first()
            return subject[0] if subject else None

    @staticmethod
    def get_subjects(
        can_select: Optional[bool],
        users: bool = False,
    ) -> Optional[list[Subject]]:
        """Get all subjects."""
        query = select(Subject)
        if can_select:
            query = query.where(Subject.can_select == can_select)
        if users:
            query = query.options(orm.subqueryload(Subject.users))
        with connect.SessionLocal() as session:
            subjects = session.execute(query).all()
            return [subject[0] for subject in subjects] if subjects else None

    @staticmethod
    def change_status_subjects(
        id: Union[bool, int],
        can_select: bool
    ) -> None:
        """Change status of subject."""
        query = update(Subject)
        query = (
            query.where(Subject.can_select == id)
            if isinstance(id, bool)
            else query.where(Subject.id == id)
        )
        query = query.values(can_select=can_select)
        with connect.SessionLocal.begin() as session:
            session.execute(query)
            session.commit()

    @staticmethod
    def create_subject(subject: dict) -> Subject:
        """Create subject."""
        with connect.SessionLocal.begin() as session:
            session.add(Subject(**subject))
            session.commit()
        return SubjectActions.get_subject(last=True)

    @staticmethod
    def delete_subject(id: int) -> None:
        """Delete subject by id."""
        with connect.SessionLocal.begin() as session:
            session.execute(
                delete(Subject).where(
                    Subject.id == id
                )
            )
