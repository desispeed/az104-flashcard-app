"""SQLite-backed de-duplication so the same mention is never alerted twice."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from .config import DATA_DIR
from .models import utcnow


class SeenStore:
    def __init__(self, path: Path | None = None):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.path = path or (DATA_DIR / "seen.db")
        self.conn = sqlite3.connect(self.path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS seen ("
            " uid TEXT PRIMARY KEY,"
            " source TEXT,"
            " url TEXT,"
            " first_seen TEXT"
            ")"
        )
        self.conn.commit()

    def is_seen(self, uid: str) -> bool:
        cur = self.conn.execute("SELECT 1 FROM seen WHERE uid = ?", (uid,))
        return cur.fetchone() is not None

    def mark_seen(self, uid: str, source: str, url: str) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO seen (uid, source, url, first_seen) VALUES (?, ?, ?, ?)",
            (uid, source, url, utcnow().isoformat()),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
