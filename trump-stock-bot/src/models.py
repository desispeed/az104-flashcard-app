"""Shared data structures."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Mention:
    """A single piece of content fetched from a source."""
    source: str          # "google_news" | "gdelt" | "truth_social"
    title: str
    text: str            # full text used for matching (title + body/summary)
    url: str
    published: datetime  # timezone-aware UTC
    raw_id: str          # source-native id (post id, article url, ...)

    @property
    def uid(self) -> str:
        """Stable id used for de-duplication across runs."""
        key = f"{self.source}:{self.raw_id}".encode("utf-8", "ignore")
        return hashlib.sha1(key).hexdigest()


@dataclass
class Signal:
    """A directional read on one company derived from a Mention."""
    mention: Mention
    ticker: str
    company: str
    direction: str       # "UP" | "DOWN" | "UNCERTAIN"
    score: int           # bullish_weight - bearish_weight (sign = direction)
    confidence: str      # "low" | "medium" | "high"
    bullish_hits: list[str] = field(default_factory=list)
    bearish_hits: list[str] = field(default_factory=list)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
