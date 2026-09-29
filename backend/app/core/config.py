"""
MarketMind AI — Core Configuration Settings (Pydantic Settings v2).
"""
import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application & Environment
    PROJECT_NAME: str = "MarketMind AI"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Server Binding
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"

    # Security & Auth
    SECRET_KEY: str = "marketmind_super_secret_jwt_key_academic_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database & TimescaleDB
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/marketmind_db"
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    # AI & Multi-Agent Keys
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # Financial Data Providers
    DEFAULT_MARKET_PROVIDER: str = "yfinance"
    ALPHA_VANTAGE_API_KEY: str = ""
    FINNHUB_API_KEY: str = ""

    # Caching & Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_ENABLED: bool = True

    # Vector Search & Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "marketmind_sec_10k"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def cors_origins(self) -> List[str]:
        return self.CORS_ORIGINS


settings = Settings()
