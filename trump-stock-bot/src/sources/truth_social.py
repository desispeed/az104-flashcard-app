"""Truth Social source via the unofficial `truthbrush` library.

Requires TRUTHSOCIAL_USERNAME / TRUTHSOCIAL_PASSWORD. This is an unofficial,
best-effort reader: Truth Social has no public API, the endpoint is rate
limited, and `truthbrush` may break when the site changes. All failures are
caught so the rest of the scan keeps working.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from ..config import Config
from ..models import Mention
from .util import strip_html, to_utc

log = logging.getLogger(__name__)

_MAX_POSTS = 40  # safety cap per scan


def _parse_created(value) -> datetime:
    if isinstance(value, datetime):
        return to_utc(value)
    if isinstance(value, str):
        try:
            return to_utc(datetime.fromisoformat(value.replace("Z", "+00:00")))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def fetch(cfg: Config) -> list[Mention]:
    if not cfg.truth_social_configured:
        log.info("Truth Social credentials not set; skipping source.")
        return []

    try:
        from truthbrush import Api
    except ImportError:
        log.warning("truthbrush not installed; skipping Truth Social. "
                    "Install with: pip install truthbrush")
        return []

    handle = cfg.truthsocial_handle
    created_after = datetime.now(timezone.utc) - timedelta(hours=cfg.lookback_hours)

    try:
        api = Api(cfg.truthsocial_username, cfg.truthsocial_password)
    except Exception as exc:
        log.error("Truth Social login failed: %s", exc)
        return []

    out: list[Mention] = []
    try:
        statuses = api.pull_statuses(
            username=handle,
            replies=False,
            created_after=created_after,
        )
        for i, post in enumerate(statuses):
            if i >= _MAX_POSTS:
                break
            post_id = str(post.get("id", ""))
            text = strip_html(post.get("content", ""))
            if not post_id or not text:
                continue
            published = _parse_created(post.get("created_at"))
            url = post.get("url") or f"https://truthsocial.com/@{handle}/posts/{post_id}"
            out.append(Mention(
                source="truth_social",
                title=text[:120],
                text=text,
                url=url,
                published=published,
                raw_id=post_id,
            ))
    except Exception as exc:
        log.error("Truth Social fetch failed: %s", exc)
        return out
    return out
