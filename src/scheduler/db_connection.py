from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from configuration import Settings

#SQL Alchemy synchronous engine
sqa_engine = create_engine(
    Settings.DB_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=sqa_engine, autoflush=False, autocommit=False)


@contextmanager
def get_session():
    """
    implement a context manager to get a session
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
