"""Database session manager."""

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import config

# Use a factory to create new database sessions
SessionFactory = sessionmaker(
    bind=create_engine(config.database.dsn, connect_args={"check_same_thread": False}),
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def create_session() -> Iterator[Session]:
    """Generator to creates a new database session.

    Yields exactly once and wrapped in a context manager to ensure proper handling.

    Try, except, finally is used to ensure the session is closed and rollback is performed
    if there is an issue during the session.

    Each request that queries the DB will have it's own session.
    """
    # Create a new session
    session = SessionFactory()
    try:
        yield session
        # Flush changes to db
        session.commit()
    except:
        # Take back any changes
        session.rollback()
    finally:
        # End the session safely
        session.close()


@contextmanager
def open_session() -> Iterator[Session]:
    """Creates a new database session with context manager.

    This ensures that the connection is properly established and closed.
    """
    return create_session()
