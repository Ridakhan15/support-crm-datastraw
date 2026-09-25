"""Database configuration: engine, session factory and the declarative Base.

The connection string comes from the DATABASE_URL environment variable, so the
same code runs on SQLite locally and PostgreSQL in production.
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

load_dotenv(override=True)  # .env always wins over a stray shell/system DATABASE_URL

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./support_crm.db")

# Some hosts (e.g. Heroku-style URLs) use "postgres://", which SQLAlchemy 2.x rejects.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

is_sqlite = DATABASE_URL.startswith("sqlite")
# "sqlite://" or "sqlite:///:memory:" (no file path) is SQLite's in-memory mode.
is_in_memory_sqlite = is_sqlite and DATABASE_URL in ("sqlite://", "sqlite:///:memory:")

# SQLite needs check_same_thread=False because FastAPI handles requests in a thread pool.
# In-memory SQLite additionally needs StaticPool: by default SQLAlchemy opens a new
# connection per checkout, and each new connection to "sqlite://" is its own separate,
# empty database. StaticPool reuses a single connection so every query sees the same
# in-memory database (this matters for the test suite and verify scripts; the real app
# uses a file-based database, where this isn't an issue).
engine_kwargs = {}
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    if is_in_memory_sqlite:
        engine_kwargs["poolclass"] = StaticPool
else:
    engine_kwargs["pool_pre_ping"] = True  # recover from dropped connections on Postgres

engine = create_engine(DATABASE_URL, **engine_kwargs)

if is_sqlite:
    # SQLite ignores foreign keys unless this is switched on for every connection.
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """FastAPI dependency: one database session per request, always closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create tables if they do not exist. Called once at application startup."""
    import app.models  # noqa: F401  (importing registers the models on Base)

    Base.metadata.create_all(bind=engine)