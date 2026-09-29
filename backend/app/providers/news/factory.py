"""
News Provider Factory.
"""
from app.providers.news.base import NewsProvider
from app.providers.news.mock_news import MockNewsProvider


def get_news_provider() -> NewsProvider:
    return MockNewsProvider()
