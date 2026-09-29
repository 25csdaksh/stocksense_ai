"""
MARKETMIND AI — Main FastAPI Application Gateway.
"""
from contextlib import asynccontextmanager
import asyncio
import json
import random
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from core.logger import logger
from core.database import init_db
from core.redis import redis_client
from api.v1.router import api_v1_router
from services.market_data_service import market_data_service, SUPPORTED_UNIVERSE


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing MARKETMIND AI platform...")
    await init_db()
    await redis_client.connect()
    logger.info("MARKETMIND AI initialized and ready to serve requests.")
    yield
    logger.info("Shutting down MARKETMIND AI platform...")
    await redis_client.disconnect()


app = FastAPI(
    title="MARKETMIND AI — Intelligence & Scenario Analysis Platform",
    description="Production-grade AI + ML + Financial Data Platform with LangGraph, RAG, and Scenario Simulators.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 Routes
app.include_router(api_v1_router)


@app.get("/health", tags=["System"])
async def health_check():
    """Returns platform operational health and runtime environment status."""
    return {
        "status": "healthy",
        "service": "MARKETMIND AI Backend",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "version": "1.0.0"
    }


# WebSocket Broadcast for Live Market Ticks
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass


ws_manager = ConnectionManager()


@app.websocket("/ws/market-feed")
async def websocket_market_feed(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Broadcast simulated high-frequency micro-ticks for monitored universe
            tickers = list(SUPPORTED_UNIVERSE.keys())
            sample_ticker = random.choice(tickers)
            quote = market_data_service.get_quote(sample_ticker)
            
            # Add minor tick fluctuation
            tick_jitter = round(random.uniform(-0.15, 0.15), 2)
            tick_payload = {
                "event": "tick",
                "ticker": sample_ticker,
                "price": round(quote["price"] + tick_jitter, 2),
                "change_pct": round(quote["change_pct"] + (tick_jitter / quote["price"]) * 100, 2),
                "volume": quote["volume"],
                "timestamp": datetime.utcnow().strftime("%H:%M:%S")
            }
            await websocket.send_text(json.dumps(tick_payload))
            await asyncio.sleep(2.5)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket feed disconnected: {e}")
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
