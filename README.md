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

The model layer uses ADK's `LiteLlm` wrapper, which lets you swap between
Gemini, Claude (Anthropic), and local models (e.g. Ollama) without changing
any tool code.

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

   > **Note:** `requirements.txt` pins `google-adk[extensions]`, not just
   > `google-adk`. The `[extensions]` extra pulls in `litellm`, which is
   > required for the `LiteLlm` model wrapper used in `agent.py`. Without it
   > you'll get:
   > `ImportError: Fail to load 'city_briefing_agent' module. LiteLLM support requires pip install google-adk[extensions]`

3. Copy `.env.example` to `city_briefing_agent/.env` and fill in:
   - Gemini API key from https://aistudio.google.com/app/apikey
     *(or an Anthropic key — see "Switching models" below)*
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

## Switching models

All three agent files (`city_briefing_agent/agent.py` and both
`sub_agents/*/agent.py`) wrap their model in `LiteLlm(...)`. To switch
providers, change the model string and make sure the matching API key is in
`city_briefing_agent/.env`:

| Provider       | Model string                                | Env var              |
|----------------|---------------------------------------------|----------------------|
| Gemini         | `LiteLlm(model="gemini/gemini-2.5-flash")`  | `GOOGLE_API_KEY`     |
| Anthropic      | `LiteLlm(model="anthropic/claude-haiku-4-5")` | `ANTHROPIC_API_KEY`  |
| Ollama (local) | `LiteLlm(model="ollama_chat/qwen2.5:7b")`   | *(none required)*    |

For Ollama, make sure the daemon is running (`ollama serve`) and the model is
pulled (`ollama pull qwen2.5:7b`) before starting the agent.

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

## Troubleshooting

- **`ImportError: ... LiteLLM support requires pip install google-adk[extensions]`**
  Your `requirements.txt` is the old version that pinned plain `google-adk`.
  Update the line to `google-adk[extensions]` and re-run
  `pip install -r requirements.txt`.

- **`ModuleNotFoundError: No module named 'city_briefing_agent'`**
  You're not running from the workspace root, or an `__init__.py` is missing.
  Run `ls` (or `dir` on Windows cmd) and confirm you see both
  `city_briefing_agent/` and `tests/`.

- **`ModuleNotFoundError: No module named 'google.adk'`**
  The venv isn't active, or `pip install -r requirements.txt` hasn't been run
  in this venv. Check with `pip list` and look for `google-adk`.

- **OpenWeather returns 401 on first run**
  New API keys can take up to an hour to activate. If news works but weather
  doesn't, wait and retry.

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
