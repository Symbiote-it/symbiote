"""
Database connection and session management for Symbiote.

Provides:
- Database engine configuration
- Session factory with context manager
- Database initialization utilities
"""
import os
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

from src.db.models import Base


# Load .env file if it exists (from project root)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


def get_database_url() -> str:
    """
    Get database URL from environment variables.
    
    Supports:
    - DATABASE_URL: Full connection string
    - Individual components: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
    """
    # Try full URL first
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # Build from components
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    user = os.getenv("DB_USER", "symbiote")
    password = os.getenv("DB_PASSWORD", "symbiote_secret")
    database = os.getenv("DB_NAME", "symbiote")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


# Create engine with connection pooling
engine = create_engine(
    get_database_url(),
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    echo=os.getenv("DB_ECHO", "false").lower() == "true"  # SQL logging
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Usage:
        with get_session() as session:
            task = Task(title="Test task")
            session.add(task)
            session.commit()
    
    Automatically handles commit/rollback and session cleanup.
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


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection for database sessions.
    Useful for FastAPI or similar frameworks.
    
    Usage:
        def get_tasks(db: Session = Depends(get_db)):
            return db.query(Task).all()
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """
    Initialize database tables.
    
    Creates all tables defined in models if they don't exist.
    Safe to call multiple times.
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")


def drop_db() -> None:
    """
    Drop all database tables.
    
    WARNING: This will delete all data. Use with caution.
    """
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped.")


def check_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        True if connection successful, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

