from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# Create engine with connection settings
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL statements in debug mode
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency injection for database session.

    Uses context manager pattern for automatic cleanup.
    The 'with' statement ensures session is properly closed
    even if an error occurs.
    """
    with Session(engine) as session:
        yield session
