"""
Fundamentals Provider Factory.
"""
from app.providers.fundamentals.base import FundamentalsProvider
from app.providers.fundamentals.mock_fundamentals import MockFundamentalsProvider


def get_fundamentals_provider() -> FundamentalsProvider:
    return MockFundamentalsProvider()
