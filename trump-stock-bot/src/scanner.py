"""Orchestrates one scan: fetch -> dedupe -> analyze -> notify."""
from __future__ import annotations

import logging

from .config import Config
from .matcher import Matcher
from .models import Signal
from .notifier import TelegramNotifier
from .sources import fetch_all
from .storage import SeenStore

log = logging.getLogger(__name__)


class Scanner:
    def __init__(self, cfg: Config, notifier: TelegramNotifier | None = None,
                 store: SeenStore | None = None):
        self.cfg = cfg
        self.matcher = Matcher(cfg.watchlist, cfg.bullish, cfg.bearish)
        self.notifier = notifier or TelegramNotifier(cfg.telegram_token, cfg.telegram_chat_id)
        self.store = store or SeenStore()

    def scan_once(self) -> list[Signal]:
        mentions = fetch_all(self.cfg)
        log.info("fetched %d mentions total", len(mentions))

        sent: list[Signal] = []
        new_count = 0
        for mention in mentions:
            if self.store.is_seen(mention.uid):
                continue
            new_count += 1
            # Mark seen up front so a transient notify error doesn't cause
            # endless re-alerting on the next run.
            self.store.mark_seen(mention.uid, mention.source, mention.url)

            for sig in self.matcher.analyze(mention):
                if self.cfg.notify_only_directional and sig.direction == "UNCERTAIN":
                    continue
                if self.notifier.send_signal(sig):
                    sent.append(sig)
                    log.info("alert: %s %s (%s) from %s",
                             sig.ticker, sig.direction, sig.confidence, sig.mention.source)

        log.info("scan complete: %d new mentions, %d alerts sent", new_count, len(sent))
        return sent
