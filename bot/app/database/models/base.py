from sqlalchemy import BigInteger, Column

from app.database.connection import Base


class BaseTable(Base):
    __abstract__ = True

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    def __repr__(self):
        columns = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return f'<{self.__tablename__}: {", ".join(map(lambda x: f"{x[0]}={x[1]}", columns.items()))}>'
