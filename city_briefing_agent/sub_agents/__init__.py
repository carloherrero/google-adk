"""Re-exports the specialist agents for clean imports from the root."""

from .weather.agent import weather_agent
from .news.agent import news_agent

__all__ = ["weather_agent", "news_agent"]
