"""Fetch top news headlines from Brave Search API and build a spoken summary."""

import os
from datetime import datetime

import requests


def fetch_news(api_key: str, query: str = "top news today",
               count: int = 5) -> list[dict]:
    """Fetch news articles from Brave Search API.

    Returns a list of article dicts with 'title', 'source', and 'description'.
    """
    url = "https://api.search.brave.com/res/v1/news/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }
    params = {
        "q": query,
        "count": count,
        "freshness": "pd",  # past day
    }

    resp = requests.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    articles = []
    for result in data.get("results", []):
        source = result.get("meta_url", {}).get("hostname", "Unknown")
        # Clean up hostname to a readable source name
        source = source.replace("www.", "").split(".")[0].title()

        articles.append({
            "title": result.get("title", ""),
            "source": source,
            "description": result.get("description", ""),
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
