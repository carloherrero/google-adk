"""Weather specialist agent definition."""

from google.adk.agents import LlmAgent

from .prompt import WEATHER_INSTRUCTION
from .tools import get_weather

from ...model_config import get_model

weather_agent = LlmAgent(
    name="weather_specialist",
    model=get_model(),
    description=(
        "Looks up current weather conditions (temperature, condition, "
        "humidity, wind) for one or more cities. Supports parallel "
        "multi-city lookups."
    ),
    instruction=WEATHER_INSTRUCTION,
    tools=[get_weather],
)
