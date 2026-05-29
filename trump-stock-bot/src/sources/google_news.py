"""Google News RSS source (free, no API key).

Runs a few Trump-business search queries and returns recent articles. The
matcher later decides which (if any) watchlist company each article concerns.

Uses stdlib XML parsing (no feedparser dependency) for easy, dependency-light
deployment.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET

import requests

from ..config import Config
from ..models import Mention
from .util import strip_html, to_utc

log = logging.getLogger(__name__)

# Broad Trump-business queries. Tweak to taste.
QUERIES = [
    "Trump company",
    "Trump stock",
    "Trump tariff",
    "Trump CEO",
    "Trump shares",
]

_RSS = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
_HEADERS = {"User-Agent": "Mozilla/5.0 (trump-stock-bot/1.0)"}


def _parse_pubdate(value: str) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return to_utc(parsedate_to_datetime(value))
    except (TypeError, ValueError):
        return datetime.now(timezone.utc)


def _fetch_feed(query: str) -> list[ET.Element]:
    url = _RSS.format(q=quote_plus(query))
    resp = requests.get(url, headers=_HEADERS, timeout=25)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    return root.findall(".//item")


def fetch(cfg: Config) -> list[Mention]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=cfg.lookback_hours)
    seen_links: set[str] = set()
    out: list[Mention] = []

    for query in QUERIES:
        try:
            items = _fetch_feed(query)
        except (requests.RequestException, ET.ParseError) as exc:
            log.warning("google_news query %r failed: %s", query, exc)
            continue

        for item in items:
            link = (item.findtext("link") or "").strip()
            if not link or link in seen_links:
                continue
            published = _parse_pubdate(item.findtext("pubDate") or "")
            if published < cutoff:
                continue
            seen_links.add(link)
            title = strip_html(item.findtext("title") or "")
            summary = strip_html(item.findtext("description") or "")
            guid = (item.findtext("guid") or link).strip()
            out.append(Mention(
                source="google_news",
                title=title,
                text=f"{title}. {summary}".strip(),
                url=link,
                published=published,
                raw_id=guid,
            ))
    return out
