"""Unit tests for the tool functions.

These test the tool functions directly (without going through the agent
or hitting real APIs), using monkeypatching to stub out the HTTP calls.

Run with:  pytest tests/
"""

from unittest.mock import MagicMock, patch

from city_briefing_agent.sub_agents.weather.tools import get_weather
from city_briefing_agent.sub_agents.news.tools import get_news


def _fake_weather_response(city_name="London", temp=60):
    """Build a fake OpenWeather API response."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "name": city_name,
        "sys": {"country": "GB"},
        "main": {"temp": temp, "feels_like": temp - 2, "humidity": 70},
        "weather": [{"description": "clear sky"}],
        "wind": {"speed": 5.0},
    }
    return response


def _fake_news_response():
    """Build a fake NewsAPI response."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "articles": [
            {
                "title": "Test headline",
                "source": {"name": "Test Source"},
                "publishedAt": "2026-05-20T10:00:00Z",
                "url": "https://example.com/article",
                "description": "A test description.",
            }
        ]
    }
    return response


class TestGetWeather:
    @patch("city_briefing_agent.sub_agents.weather.tools.requests.get")
    @patch.dict("os.environ", {"OPENWEATHER_API_KEY": "fake"})
    def test_single_city_string(self, mock_get):
        mock_get.return_value = _fake_weather_response("London", 60)
        result = get_weather("London")
        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["city"] == "London"
        assert result["results"][0]["temp"] == "60°F"

    @patch("city_briefing_agent.sub_agents.weather.tools.requests.get")
    @patch.dict("os.environ", {"OPENWEATHER_API_KEY": "fake"})
    def test_multi_city_list(self, mock_get):
        mock_get.side_effect = [
            _fake_weather_response("Tokyo", 75),
            _fake_weather_response("Paris", 55),
            _fake_weather_response("London", 60),
        ]
        result = get_weather(["Tokyo", "Paris", "London"])
        assert len(result["results"]) == 3

    def test_missing_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
        result = get_weather("London")
        assert "error" in result["results"][0]
        assert "OPENWEATHER_API_KEY" in result["results"][0]["error"]

    @patch("city_briefing_agent.sub_agents.weather.tools.requests.get")
    @patch.dict("os.environ", {"OPENWEATHER_API_KEY": "fake"})
    def test_city_not_found(self, mock_get):
        response = MagicMock()
        response.status_code = 404
        mock_get.return_value = response
        result = get_weather("Notarealcity")
        assert "error" in result["results"][0]
        assert "not found" in result["results"][0]["error"].lower()

    def test_empty_list(self):
        result = get_weather([])
        assert result["results"] == []
        assert "error" in result


class TestGetNews:
    @patch("city_briefing_agent.sub_agents.news.tools.requests.get")
    @patch.dict("os.environ", {"NEWSAPI_KEY": "fake"})
    def test_single_topic(self, mock_get):
        mock_get.return_value = _fake_news_response()
        result = get_news("AI")
        assert len(result["results"]) == 1
        assert result["results"][0]["topic"] == "AI"
        assert len(result["results"][0]["articles"]) == 1

    @patch("city_briefing_agent.sub_agents.news.tools.requests.get")
    @patch.dict("os.environ", {"NEWSAPI_KEY": "fake"})
    def test_rate_limit(self, mock_get):
        response = MagicMock()
        response.status_code = 429
        mock_get.return_value = response
        result = get_news("AI")
        assert "error" in result["results"][0]
        assert "rate limit" in result["results"][0]["error"].lower()
