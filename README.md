# City Briefing Agent

A multi-agent system built with Google's Agent Development Kit (ADK) that
provides weather and news briefings for any city or topic.

## Architecture

```
city_briefing_bot (root)
├── weather_specialist  → get_weather (OpenWeatherMap)
└── news_specialist     → get_news    (NewsAPI)
```

The root agent routes queries to one or both specialists. Each specialist's
tool supports parallel multi-item lookups (e.g. weather for Tokyo + Paris +
London in one round-trip).

## Setup

1. Create and activate a virtual environment (one level above the agent folder):
   ```bash
   python -m venv .venv
   # Windows (Git Bash):  source .venv/Scripts/activate
   # Windows (PS):        .venv\Scripts\Activate.ps1
   # macOS/Linux:         source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `city_briefing_agent/.env` and fill in:
   - Gemini API key from https://aistudio.google.com/app/apikey
   - OpenWeatherMap key from https://home.openweathermap.org/api_keys
   - NewsAPI key from https://newsapi.org/register

## Running

From the workspace root (one level above `city_briefing_agent/`):

```bash
# Terminal chat
adk run city_briefing_agent

# Browser UI (recommended — shows reasoning + tool calls)
adk web
```

## Example prompts

- `What's the weather in London?`
- `Compare the weather in Tokyo, Paris, and New York`
- `Latest news on AI`
- `Give me a briefing on Tokyo` (weather + news)
- `Briefing on Tokyo, Paris, and São Paulo`

## Testing

The unit tests mock out the HTTP layer, so they run without API keys and don't
burn your free-tier quota.

1. Install dev dependencies (one-time):
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run the tests from the workspace root:
   ```bash
   pytest
   ```

   Coverage and verbose output are enabled by default via `pyproject.toml`,
   so you'll see which lines of `city_briefing_agent/` are exercised.

3. (Optional) Generate an HTML coverage report:
   ```bash
   pytest --cov-report=html
   # then open htmlcov/index.html in a browser
   ```

### Common test failures

- **`ModuleNotFoundError: No module named 'city_briefing_agent'`** — you're not
  at the workspace root, or an `__init__.py` is missing. Run `ls` (or `dir`)
  and confirm you see both `city_briefing_agent/` and `tests/`.
- **`ModuleNotFoundError: No module named 'google.adk'`** — the venv isn't
  active, or `pip install -r requirements.txt` hasn't been run in this venv.

## Project structure

```
your-workspace/
├── .venv/                       # virtual environment (gitignored)
├── .env.example                 # template for required API keys
├── .gitignore
├── requirements.txt             # runtime dependencies
├── requirements-dev.txt         # test/dev dependencies
├── pyproject.toml               # pytest + coverage config
├── README.md                    # this file
│
├── city_briefing_agent/
│   ├── agent.py                 # root_agent
│   ├── prompt.py                # root instruction
│   ├── .env                     # your real API keys (gitignored)
│   ├── sub_agents/
│   │   ├── weather/             # weather specialist + its tool
│   │   └── news/                # news specialist + its tool
│   └── eval/                    # ADK eval sets
│
└── tests/
    └── test_tools.py            # unit tests (mocked HTTP)
```
