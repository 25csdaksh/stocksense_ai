"""
SQLAlchemy Async Database Connection and Session Management.
Supports PostgreSQL (with TimescaleDB) and SQLite for local development.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config import settings
from core.logger import logger

# Construct Async SQLAlchemy Engine
# Handles both postgresql+asyncpg:// and sqlite+aiosqlite:///
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency for database session injection."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """Initializes database tables if not existing."""
    try:
        async with engine.begin() as conn:
            # Import models so Base has metadata registered
            import models.asset
            import models.price_history
            import models.fundamentals
            import models.anomaly
            import models.simulation
            
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database schemas initialized successfully.")
    except Exception as e:
        logger.warning(f"Database initialization notice: {e}")
