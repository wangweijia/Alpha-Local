from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


_engine = None
_SessionFactory: sessionmaker[Session] | None = None


def configure_database(database_url: str):
    global _engine, _SessionFactory
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    _engine = create_engine(database_url, connect_args=connect_args)
    _SessionFactory = sessionmaker(bind=_engine, autoflush=False, autocommit=False, expire_on_commit=False)
    return _engine


def init_database() -> None:
    if _engine is None:
        raise RuntimeError("Database engine has not been configured.")
    Base.metadata.create_all(bind=_engine)


def get_session_factory() -> sessionmaker[Session]:
    if _SessionFactory is None:
        raise RuntimeError("Database session factory has not been configured.")
    return _SessionFactory


def get_session() -> Generator[Session, None, None]:
    if _SessionFactory is None:
        raise RuntimeError("Database session factory has not been configured.")
    session = _SessionFactory()
    try:
        yield session
    finally:
        session.close()
