import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=True,
    bind=engine,
    expire_on_commit=False,
    future=True,
)
Base = declarative_base()


def init_db():
    """Init db, create tables."""
    Base.metadata.create_all(bind=engine)
