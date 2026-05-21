"""News tool — fetches recent headlines from NewsAPI.

Supports single or multi-topic lookups. Multi-topic lookups run in
parallel via a thread pool.
"""

import concurrent.futures
import os
from typing import List, Union

import requests

NEWSAPI_URL = "https://newsapi.org/v2/everything"
TIMEOUT_SECONDS = 10
MAX_PARALLEL = 8
ARTICLES_PER_TOPIC = 5


def _fetch_one_news(topic: str) -> dict:
    """Fetch recent headlines for a single topic. Always returns a dict."""
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        return {"topic": topic, "error": "NEWSAPI_KEY not set in .env"}

    try:
        response = requests.get(
            NEWSAPI_URL,
            params={
                "q": topic,
                "apiKey": api_key,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": ARTICLES_PER_TOPIC,
            },
            timeout=TIMEOUT_SECONDS,
        )
    except requests.RequestException as e:
        return {"topic": topic, "error": f"Network error: {e}"}

    if response.status_code == 401:
        return {"topic": topic, "error": "Invalid NewsAPI key."}
    if response.status_code == 429:
        return {
            "topic": topic,
            "error": "NewsAPI rate limit exceeded for today.",
        }
    if response.status_code != 200:
        return {
            "topic": topic,
            "error": f"NewsAPI returned status {response.status_code}.",
        }

    data = response.json()
    articles = [
        {
            "title": a.get("title"),
            "source": (a.get("source") or {}).get("name"),
            "published": a.get("publishedAt"),
            "url": a.get("url"),
            "description": a.get("description"),
        }
        for a in data.get("articles", [])[:ARTICLES_PER_TOPIC]
    ]
    return {"topic": topic, "articles": articles}


def get_news(topics: Union[str, List[str]]) -> dict:
    """Get the latest news headlines for one or more topics, in parallel.

    Args:
        topics: A single topic/keyword (e.g. "AI", "Tokyo", "climate") OR
            a list of topics. When multiple are given, lookups run
            concurrently. Topics can be cities, keywords, people,
            companies — anything you'd type into a news search.

    Returns:
        A dictionary with a 'results' key containing one entry per topic.
        Each entry has a 'topic' field and either an 'articles' list
        (each with title, source, published, url, description) or an
        'error' key explaining what went wrong.
    """
    topic_list = [topics] if isinstance(topics, str) else list(topics)

    if not topic_list:
        return {"results": [], "error": "No topics provided."}

    worker_count = min(MAX_PARALLEL, len(topic_list))
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as pool:
        results = list(pool.map(_fetch_one_news, topic_list))

    return {"results": results}
