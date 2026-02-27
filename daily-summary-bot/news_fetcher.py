"""Fetch top news headlines from NewsAPI and build a spoken summary."""

import os
from datetime import datetime

import requests


def fetch_news(api_key: str, country: str = "us", category: str = "general",
               max_articles: int = 5) -> list[dict]:
    """Fetch top headlines from NewsAPI.

    Returns a list of article dicts with 'title', 'source', and 'description'.
    """
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": api_key,
        "country": country,
        "category": category,
        "pageSize": max_articles,
    }

    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "ok":
        raise RuntimeError(f"NewsAPI error: {data.get('message', 'Unknown error')}")

    articles = []
    for article in data.get("articles", []):
        articles.append({
            "title": article.get("title", ""),
            "source": article.get("source", {}).get("name", "Unknown"),
            "description": article.get("description") or "",
        })

    return articles


def build_summary_text(articles: list[dict]) -> str:
    """Turn a list of articles into a natural-sounding script for TTS."""
    today = datetime.now().strftime("%A, %B %d, %Y")

    lines = [
        f"Good morning! Here is your daily news summary for {today}.",
        "",
    ]

    for i, article in enumerate(articles, 1):
        title = article["title"]
        source = article["source"]
        description = article["description"]

        lines.append(f"Story number {i}. From {source}.")
        lines.append(f"{title}.")
        if description:
            lines.append(f"{description}")
        lines.append("")

    lines.append("That's all for today's news. Have a great day!")

    return "\n".join(lines)
