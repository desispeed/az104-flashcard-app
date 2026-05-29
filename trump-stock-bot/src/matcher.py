"""Rule-based company detection + bullish/bearish scoring.

No external services: a Mention's text is scanned for watchlist company
aliases, and for each company found the surrounding text is scored against
weighted bullish / bearish keyword stems to produce a directional Signal.
"""
from __future__ import annotations

import re

from .models import Mention, Signal


def _compile_alias(alias: str) -> re.Pattern:
    # Whole-word / whole-phrase, case-insensitive. Internal whitespace in a
    # phrase is allowed to be any run of whitespace.
    parts = [re.escape(tok) for tok in alias.split()]
    pattern = r"\b" + r"\s+".join(parts) + r"\b"
    return re.compile(pattern, re.IGNORECASE)


def _compile_stem(stem: str) -> re.Pattern:
    # Match the stem as a word prefix so "tariff" also hits "tariffs",
    # "investigat" hits "investigate/investigation", etc.
    parts = [re.escape(tok) for tok in stem.split()]
    pattern = r"\b" + r"\s+".join(parts) + r"\w*"
    return re.compile(pattern, re.IGNORECASE)


class Matcher:
    def __init__(self, watchlist: list[dict], bullish: list[dict], bearish: list[dict]):
        self.companies = []
        for c in watchlist:
            aliases = c.get("aliases") or [c.get("name", "")]
            compiled = [(_compile_alias(a), a) for a in aliases if a]
            self.companies.append({
                "ticker": c.get("ticker", "?"),
                "name": c.get("name", c.get("ticker", "?")),
                "aliases": compiled,
            })
        self.bullish = [(_compile_stem(k["stem"]), k["stem"], int(k.get("weight", 1))) for k in bullish]
        self.bearish = [(_compile_stem(k["stem"]), k["stem"], int(k.get("weight", 1))) for k in bearish]

    def _score(self, text: str, keywords) -> tuple[int, list[str]]:
        total = 0
        hits: list[str] = []
        for pattern, stem, weight in keywords:
            n = len(pattern.findall(text))
            if n:
                total += weight * n
                hits.append(stem)
        return total, hits

    @staticmethod
    def _confidence(margin: int, total_hits: int) -> str:
        if margin >= 4 or total_hits >= 5:
            return "high"
        if margin >= 2 or total_hits >= 3:
            return "medium"
        return "low"

    def analyze(self, mention: Mention) -> list[Signal]:
        text = mention.text or mention.title
        if not text:
            return []

        bull_score, bull_hits = self._score(text, self.bullish)
        bear_score, bear_hits = self._score(text, self.bearish)

        signals: list[Signal] = []
        for company in self.companies:
            mentioned = any(p.search(text) for p, _ in company["aliases"])
            if not mentioned:
                continue

            score = bull_score - bear_score
            if score > 0:
                direction = "UP"
            elif score < 0:
                direction = "DOWN"
            else:
                direction = "UNCERTAIN"

            confidence = self._confidence(abs(score), bull_score + bear_score)
            signals.append(Signal(
                mention=mention,
                ticker=company["ticker"],
                company=company["name"],
                direction=direction,
                score=score,
                confidence=confidence,
                bullish_hits=bull_hits,
                bearish_hits=bear_hits,
            ))
        return signals
