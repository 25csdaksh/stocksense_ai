"""
Async Database Engine, Session Factory, and Dependency Injection for SQLAlchemy 2.0.
"""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from app.core.config import settings
from app.core.logging import logger
from app.db.base import Base

# Determine engine parameters based on database dialect (PostgreSQL pool vs SQLite for local tests)
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine_kwargs = {
    "echo": settings.DB_ECHO,
    "future": True,
}

if not _is_sqlite:
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_pre_ping": True,
    })

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency yielding an asynchronous SQLAlchemy database session.
    Automatically commits on success or rolls back on unhandled exceptions.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db(custom_engine: Optional[AsyncEngine] = None):
    """Initializes database tables (useful for development and automated tests)."""
    target_engine = custom_engine or engine
    try:
        async with target_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized successfully.")
    except Exception as err:
        logger.warning(f"Database initialization warning: {err}")


async def close_db():
    """Disposes database connection pool during application shutdown."""
    if engine:
        await engine.dispose()
        logger.info("Database connection pool closed.")
