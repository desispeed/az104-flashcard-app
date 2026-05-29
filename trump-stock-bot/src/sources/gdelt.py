"""GDELT 2.0 DOC API source (free, no API key).

Returns recent English-language news articles mentioning Trump. GDELT only
exposes article titles here, so matching relies on the headline.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import requests

from ..config import Config
from ..models import Mention
from .util import strip_html, to_utc

log = logging.getLogger(__name__)

_API = "https://api.gdeltproject.org/api/v2/doc/doc"
_QUERY = '"Donald Trump" sourcelang:english'


def _parse_seendate(value: str) -> datetime:
    # GDELT format: 20260529T140000Z
    try:
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


def fetch(cfg: Config) -> list[Mention]:
    timespan = f"{max(cfg.lookback_hours, 1)}h"
    params = {
        "query": _QUERY,
        "mode": "ArtList",
        "format": "json",
        "timespan": timespan,
        "maxrecords": 75,
        "sort": "DateDesc",
    }
    resp = requests.get(_API, params=params, timeout=25,
                        headers={"User-Agent": "trump-stock-bot/1.0"})
    resp.raise_for_status()
    # GDELT sometimes returns empty body or HTML on throttling.
    try:
        data = resp.json()
    except ValueError:
        log.warning("GDELT returned non-JSON (likely throttled); skipping.")
        return []

    out: list[Mention] = []
    for art in data.get("articles", []):
        url = art.get("url", "")
        title = strip_html(art.get("title", ""))
        if not url or not title:
            continue
        published = to_utc(_parse_seendate(art.get("seendate", "")))
        out.append(Mention(
            source="gdelt",
            title=title,
            text=title,
            url=url,
            published=published,
            raw_id=url,
        ))
    return out
