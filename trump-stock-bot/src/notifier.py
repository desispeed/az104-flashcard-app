"""Telegram delivery of signals."""
from __future__ import annotations

import logging

import requests

from .models import Signal

log = logging.getLogger(__name__)

DISCLAIMER = "⚠️ Informational only — not financial advice. Rule-based keyword guess."

_ARROW = {"UP": "📈", "DOWN": "📉", "UNCERTAIN": "❓"}
_SOURCE_LABEL = {
    "google_news": "Google News",
    "gdelt": "GDELT",
    "truth_social": "Truth Social",
}


def _escape_md(text: str) -> str:
    # Telegram "Markdown" (legacy) — escape the few chars that break parsing.
    for ch in ("_", "*", "`", "["):
        text = text.replace(ch, "\\" + ch)
    return text


def format_signal(sig: Signal) -> str:
    m = sig.mention
    arrow = _ARROW.get(sig.direction, "❓")
    verb = {"UP": "LIKELY UP", "DOWN": "LIKELY DOWN", "UNCERTAIN": "UNCLEAR"}[sig.direction]
    source = _SOURCE_LABEL.get(m.source, m.source)

    reasons = []
    if sig.bullish_hits:
        reasons.append("bullish: " + ", ".join(sig.bullish_hits[:6]))
    if sig.bearish_hits:
        reasons.append("bearish: " + ", ".join(sig.bearish_hits[:6]))
    why = " | ".join(reasons) if reasons else "company named, no strong sentiment terms"

    snippet = (m.text or m.title).strip().replace("\n", " ")
    if len(snippet) > 280:
        snippet = snippet[:277] + "..."

    lines = [
        "🚨 *Trump Stock Signal*",
        "",
        f"{arrow} *{_escape_md(sig.ticker)}* — {_escape_md(sig.company)}",
        f"Direction: *{verb}*  (confidence: {sig.confidence})",
        f"Source: {source}",
        f"Why: {_escape_md(why)}",
        "",
        f"_{_escape_md(snippet)}_",
        "",
        f"🔗 {m.url}",
        f"🕒 {m.published.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        DISCLAIMER,
    ]
    return "\n".join(lines)


class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.api = f"https://api.telegram.org/bot{token}"

    def send(self, text: str) -> bool:
        if not self.token or not self.chat_id:
            log.warning("Telegram not configured; would have sent:\n%s", text)
            return False
        try:
            resp = requests.post(
                f"{self.api}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False,
                },
                timeout=20,
            )
            if resp.status_code != 200:
                log.error("Telegram send failed (%s): %s", resp.status_code, resp.text)
                return False
            return True
        except requests.RequestException as exc:
            log.error("Telegram request error: %s", exc)
            return False

    def send_signal(self, sig: Signal) -> bool:
        return self.send(format_signal(sig))
