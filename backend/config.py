"""
MARKETMIND AI — Application Configuration & Environment Settings
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Application Mode
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server Gateway
    BACKEND_HOST: str = Field(default="0.0.0.0", env="BACKEND_HOST")
    BACKEND_PORT: int = Field(default=8000, env="BACKEND_PORT")
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        env="ALLOWED_ORIGINS"
    )

    # Persistence: PostgreSQL / TimescaleDB
    POSTGRES_USER: str = Field(default="marketmind_admin", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="marketmind_secret", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="marketmind_db", env="POSTGRES_DB")
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./marketmind.db",  # Fallback for lightweight local standalone dev
        env="DATABASE_URL"
    )

    # Redis Cache & Pub/Sub
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # Qdrant Vector Database
    QDRANT_HOST: str = Field(default="localhost", env="QDRANT_HOST")
    QDRANT_PORT: int = Field(default=6333, env="QDRANT_PORT")
    QDRANT_GRPC_PORT: int = Field(default=6334, env="QDRANT_GRPC_PORT")
    QDRANT_API_KEY: str = Field(default="", env="QDRANT_API_KEY")

    # AI & Multi-Agent (Google Gemini)
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(default="gemini-1.5-pro", env="GEMINI_MODEL")

    # Financial Data APIs & Market Providers (Phase 6)
    DEFAULT_MARKET_PROVIDER: str = Field(default="auto", env="DEFAULT_MARKET_PROVIDER")
    MARKET_DATA_PROVIDER: str = Field(default="auto", env="MARKET_DATA_PROVIDER")
    INDIA_MARKET_PROVIDER: str = Field(default="indian", env="INDIA_MARKET_PROVIDER")
    US_MARKET_PROVIDER: str = Field(default="yfinance", env="US_MARKET_PROVIDER")
    ALPHA_VANTAGE_API_KEY: str = Field(default="", env="ALPHA_VANTAGE_API_KEY")
    FINNHUB_API_KEY: str = Field(default="", env="FINNHUB_API_KEY")
    POLYGON_API_KEY: str = Field(default="", env="POLYGON_API_KEY")

    # Indian Broker Credentials (Optional / Future Licensed Integrations)
    ZERODHA_API_KEY: str = Field(default="", env="ZERODHA_API_KEY")
    ZERODHA_API_SECRET: str = Field(default="", env="ZERODHA_API_SECRET")
    ZERODHA_ACCESS_TOKEN: str = Field(default="", env="ZERODHA_ACCESS_TOKEN")
    UPSTOX_API_KEY: str = Field(default="", env="UPSTOX_API_KEY")
    UPSTOX_API_SECRET: str = Field(default="", env="UPSTOX_API_SECRET")
    UPSTOX_ACCESS_TOKEN: str = Field(default="", env="UPSTOX_ACCESS_TOKEN")
    ANGEL_API_KEY: str = Field(default="", env="ANGEL_API_KEY")
    ANGEL_CLIENT_ID: str = Field(default="", env="ANGEL_CLIENT_ID")
    ANGEL_PASSWORD: str = Field(default="", env="ANGEL_PASSWORD")
    ANGEL_TOTP: str = Field(default="", env="ANGEL_TOTP")

    # Observability
    LANGFUSE_PUBLIC_KEY: str = Field(default="", env="LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY: str = Field(default="", env="LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST: str = Field(default="https://cloud.langfuse.com", env="LANGFUSE_HOST")

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
