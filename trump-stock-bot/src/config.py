"""Configuration loading from environment + JSON config files."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:  # python-dotenv is optional at runtime
    pass

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"


def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, "").strip())
    except (ValueError, AttributeError):
        return default


@dataclass
class Config:
    telegram_token: str
    telegram_chat_id: str
    truthsocial_username: str
    truthsocial_password: str
    truthsocial_handle: str
    lookback_hours: int
    scan_interval_seconds: int
    enabled_sources: list[str]
    notify_only_directional: bool
    watchlist: list[dict]
    bullish: list[dict]
    bearish: list[dict]

    @property
    def truth_social_configured(self) -> bool:
        return bool(self.truthsocial_username and self.truthsocial_password)


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_config() -> Config:
    watchlist = _load_json(CONFIG_DIR / "watchlist.json").get("companies", [])
    keywords = _load_json(CONFIG_DIR / "keywords.json")

    enabled = [
        s.strip()
        for s in os.getenv("ENABLED_SOURCES", "google_news,gdelt,truth_social").split(",")
        if s.strip()
    ]

    return Config(
        telegram_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
        truthsocial_username=os.getenv("TRUTHSOCIAL_USERNAME", "").strip(),
        truthsocial_password=os.getenv("TRUTHSOCIAL_PASSWORD", "").strip(),
        truthsocial_handle=os.getenv("TRUTHSOCIAL_HANDLE", "realDonaldTrump").strip().lstrip("@"),
        lookback_hours=_env_int("LOOKBACK_HOURS", 1),
        scan_interval_seconds=_env_int("SCAN_INTERVAL_SECONDS", 3600),
        enabled_sources=enabled,
        notify_only_directional=_env_bool("NOTIFY_ONLY_DIRECTIONAL", True),
        watchlist=watchlist,
        bullish=keywords.get("bullish", []),
        bearish=keywords.get("bearish", []),
    )
