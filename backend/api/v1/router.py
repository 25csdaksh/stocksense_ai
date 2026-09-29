"""
Master API v1 Router Aggregator.
"""
from fastapi import APIRouter

from api.v1.market import router as market_router
from api.v1.fundamentals import router as fundamentals_router
from api.v1.anomalies import router as anomalies_router
from api.v1.correlations import router as correlations_router
from api.v1.scenario import router as scenario_router
from api.v1.research import router as research_router
from api.v1.agent import router as agent_router
from api.v1.portfolio import router as portfolio_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(market_router)
api_v1_router.include_router(fundamentals_router)
api_v1_router.include_router(anomalies_router)
api_v1_router.include_router(correlations_router)
api_v1_router.include_router(scenario_router)
api_v1_router.include_router(research_router)
api_v1_router.include_router(agent_router)
api_v1_router.include_router(portfolio_router)

__all__ = ["api_v1_router"]
