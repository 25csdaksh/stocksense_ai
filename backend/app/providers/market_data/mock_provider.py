"""
MarketMind AI — High-Fidelity Synthetic Market Data Provider Adapter.
Phase 6.1: Subclasses DemoMarketProvider with is_synthetic=True for transparent academic sandbox development.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.providers.market_data.demo_provider import DemoMarketProvider
from app.utils.constants import DEFAULT_INDICES


class MockMarketProvider(DemoMarketProvider):
    """
    Backward-compatible synthetic mock provider.
    Subclasses DemoMarketProvider to satisfy the complete MarketDataProvider interface.
    """
    def __init__(self):
        super().__init__()
        self.provider_name = "MockMarketProvider"


mock_market_provider = MockMarketProvider()
