from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings
import logging

# Set up logging for database operations
logger = logging.getLogger(__name__)

# Create our async database engine
# The echo flag is set to True for development to help us see SQL queries
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
    pool_size=5,  # Reasonable default for a home application
    max_overflow=10  # Allow some additional connections during peak usage
)

# Create an async session factory that we'll use to interact with the database
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # This prevents unexpected behavior with async operations
    autoflush=True
)

# Create a base class for our SQLAlchemy models
Base = declarative_base()

# Dependency that will manage database sessions for our API endpoints
async def get_db():
    """
    Creates a database session for each request and ensures proper cleanup.
    This function works as a FastAPI dependency that will be injected into our routes.
    The session is automatically closed when the request is complete.
    """
    session = AsyncSessionLocal()
    try:
        logger.debug("Creating new database session")
        yield session
        await session.commit()
        logger.debug("Database session committed successfully")
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session rolled back due to error: {str(e)}")
        raise
    finally:
        await session.close()
        logger.debug("Database session closed")