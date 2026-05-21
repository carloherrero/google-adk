"""Root agent for the city briefing system.

The architecture branches based on LLM_PROVIDER in .env:

  - Cloud models (Gemini, Claude) and large local models (14B+):
    NESTED — root routes to weather_specialist / news_specialist via
    AgentTool. Cleaner separation of concerns.

  - Small local models (Ollama 7B):
    FLAT — root agent calls get_weather / get_news directly. Avoids
    the two-layer AgentTool pattern that confuses smaller models.

Same agent file, two architectures. Just change .env.
"""

from google.adk.agents import LlmAgent

from .model_config import get_model, USE_NESTED_AGENTS
from .prompt import ROOT_INSTRUCTION_NESTED, ROOT_INSTRUCTION_FLAT


if USE_NESTED_AGENTS:
    # ──────────────────────────────────────────────────────────────
    # Nested architecture — root delegates to specialist agents
    # ──────────────────────────────────────────────────────────────
    from google.adk.tools.agent_tool import AgentTool
    from .sub_agents import weather_agent, news_agent

    root_agent = LlmAgent(
        name="city_briefing_bot",
        model=get_model(),
        description=(
            "A briefing assistant that provides current weather and the latest "
            "news for any city, topic, or combination thereof."
        ),
        instruction=ROOT_INSTRUCTION_NESTED,
        tools=[
            AgentTool(agent=weather_agent),
            AgentTool(agent=news_agent),
        ],
    )

else:
    # ──────────────────────────────────────────────────────────────
    # Flat architecture — root calls tool functions directly
    # ──────────────────────────────────────────────────────────────
    from .sub_agents.weather.tools import get_weather
    from .sub_agents.news.tools import get_news

    root_agent = LlmAgent(
        name="city_briefing_bot",
        model=get_model(),
        description=(
            "A briefing assistant that provides current weather and the latest "
            "news for any city, topic, or combination thereof."
        ),
        instruction=ROOT_INSTRUCTION_FLAT,
        tools=[get_weather, get_news],
    )
