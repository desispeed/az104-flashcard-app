"""Content sources. Each exposes fetch(cfg) -> list[Mention]."""
from __future__ import annotations

import logging

from ..config import Config
from ..models import Mention
from . import gdelt, google_news, truth_social

log = logging.getLogger(__name__)

_REGISTRY = {
    "google_news": google_news.fetch,
    "gdelt": gdelt.fetch,
    "truth_social": truth_social.fetch,
}


def fetch_all(cfg: Config) -> list[Mention]:
    mentions: list[Mention] = []
    for name in cfg.enabled_sources:
        fn = _REGISTRY.get(name)
        if not fn:
            log.warning("Unknown source '%s' — skipping.", name)
            continue
        try:
            got = fn(cfg)
            log.info("source %s -> %d mentions", name, len(got))
            mentions.extend(got)
        except Exception as exc:  # one bad source must not kill the scan
            log.error("source %s failed: %s", name, exc)
    return mentions
