"""News specialist agent definition."""

from google.adk.agents import LlmAgent

from .prompt import NEWS_INSTRUCTION
from .tools import get_news

from ...model_config import get_model

news_agent = LlmAgent(
    name="news_specialist",
    model=get_model(),
    description=(
        "Fetches the latest news headlines for one or more topics, "
        "keywords, places, or people. Supports parallel multi-topic "
        "lookups."
    ),
    instruction=NEWS_INSTRUCTION,
    tools=[get_news],
)
