"""
MarketMind AI — FastAPI Backend Application Entry Point.
AI-Powered Stock Market Intelligence & Scenario Analysis Platform.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import (
    MarketMindException,
    marketmind_exception_handler,
    generic_exception_handler
)
from app.cache.redis_client import redis_client

# Route Imports
from app.api.routes import (
    auth,
    market,
    stocks,
    fundamentals,
    news,
    analytics,
    anomalies,
    scenarios,
    portfolio,
    watchlist,
    research,
    ai,
    health
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle hooks."""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    await redis_client.connect()
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")
    await redis_client.disconnect()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Stock Market Intelligence, RAG Regulatory Search & Stochastic Scenario Analysis Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(MarketMindException, marketmind_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# API Version 1 Master Router
api_v1_router = APIRouter(prefix=settings.API_V1_PREFIX)

api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(market.router)
api_v1_router.include_router(stocks.router)
api_v1_router.include_router(fundamentals.router)
api_v1_router.include_router(news.router)
api_v1_router.include_router(analytics.router)
api_v1_router.include_router(anomalies.router)
api_v1_router.include_router(scenarios.router)
api_v1_router.include_router(portfolio.router)
api_v1_router.include_router(watchlist.router)
api_v1_router.include_router(research.router)
api_v1_router.include_router(ai.router)

# Mount Routers
app.include_router(api_v1_router)
app.include_router(health.router)  # Also expose /health at root


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "api_v1": settings.API_V1_PREFIX,
        "health": "/health"
    }
