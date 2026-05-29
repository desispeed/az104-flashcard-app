"""Interactive Telegram bot: long-polls for commands AND runs periodic scans
in one single-threaded loop (no extra dependencies).

Only the configured TELEGRAM_CHAT_ID may issue commands — messages from any
other chat are ignored, so the bot can't be driven by strangers.
"""
from __future__ import annotations

import logging
import time

import requests

from .config import Config, save_watchlist
from .models import utcnow
from .scanner import Scanner

log = logging.getLogger(__name__)

LONG_POLL_TIMEOUT = 30  # seconds Telegram holds the getUpdates request open

HELP_TEXT = (
    "🤖 *Trump Stock Tracker* — commands:\n\n"
    "/scan — run a scan right now\n"
    "/watchlist — list tracked companies\n"
    "/add `TICKER Name; alias; alias` — track a company\n"
    "/remove `TICKER` — stop tracking a company\n"
    "/status — uptime, last/next scan, alert counts\n"
    "/sources — which sources are enabled\n"
    "/settings — current configuration\n"
    "/help — this message\n\n"
    "_Alerts are a rule-based keyword guess — not financial advice._"
)


class TelegramBot:
    def __init__(self, cfg: Config, scanner: Scanner | None = None):
        self.cfg = cfg
        self.scanner = scanner or Scanner(cfg)
        self.notifier = self.scanner.notifier
        self.api = f"https://api.telegram.org/bot{cfg.telegram_token}"
        self.offset = None            # getUpdates pagination cursor
        self.started_at = utcnow()
        self.next_scan_at = time.monotonic()  # scan ASAP on startup

    # ── Telegram I/O ────────────────────────────────────────────────────
    def _reply(self, chat_id: str, text: str, markdown: bool = True) -> None:
        self.notifier.send(text, chat_id=chat_id, markdown=markdown)

    def _drain_backlog(self) -> None:
        """Skip commands sent while the bot was offline."""
        try:
            resp = requests.get(f"{self.api}/getUpdates",
                                params={"timeout": 0, "offset": -1}, timeout=15)
            data = resp.json()
            results = data.get("result", [])
            if results:
                self.offset = results[-1]["update_id"] + 1
                log.info("skipped %d backlog update(s)", len(results))
        except (requests.RequestException, ValueError) as exc:
            log.warning("could not drain backlog: %s", exc)

    def _poll(self) -> list[dict]:
        params = {"timeout": LONG_POLL_TIMEOUT}
        if self.offset is not None:
            params["offset"] = self.offset
        try:
            resp = requests.get(f"{self.api}/getUpdates", params=params,
                                timeout=LONG_POLL_TIMEOUT + 10)
            data = resp.json()
        except (requests.RequestException, ValueError) as exc:
            log.warning("getUpdates failed: %s", exc)
            time.sleep(5)
            return []
        if not data.get("ok"):
            log.warning("getUpdates not ok: %s", data)
            return []
        updates = data.get("result", [])
        if updates:
            self.offset = updates[-1]["update_id"] + 1
        return updates

    # ── command handling ────────────────────────────────────────────────
    def _handle_update(self, update: dict) -> None:
        msg = update.get("message") or update.get("edited_message")
        if not msg:
            return
        chat_id = str((msg.get("chat") or {}).get("id", ""))
        text = (msg.get("text") or "").strip()
        if not text:
            return

        # Authorization: only the configured chat may command the bot.
        if self.cfg.telegram_chat_id and chat_id != self.cfg.telegram_chat_id:
            log.warning("ignoring command from unauthorized chat %s", chat_id)
            self._reply(chat_id, "⛔ Not authorized.", markdown=False)
            return

        # "/cmd@BotName arg" -> command="scan", args="arg"
        parts = text.split(maxsplit=1)
        command = parts[0].lstrip("/").split("@")[0].lower()
        args = parts[1].strip() if len(parts) > 1 else ""

        handler = {
            "start": self._cmd_help,
            "help": self._cmd_help,
            "scan": self._cmd_scan,
            "watchlist": self._cmd_watchlist,
            "add": self._cmd_add,
            "remove": self._cmd_remove,
            "status": self._cmd_status,
            "sources": self._cmd_sources,
            "settings": self._cmd_settings,
        }.get(command)

        if handler is None:
            self._reply(chat_id, f"Unknown command: /{command}\nTry /help")
            return
        try:
            handler(chat_id, args)
        except Exception as exc:  # never let one command kill the loop
            log.exception("command /%s failed", command)
            self._reply(chat_id, f"⚠️ Command failed: {exc}", markdown=False)

    def _cmd_help(self, chat_id: str, args: str) -> None:
        self._reply(chat_id, HELP_TEXT)

    def _cmd_scan(self, chat_id: str, args: str) -> None:
        self._reply(chat_id, "🔍 Scanning now…")
        sent = self.scanner.scan_once()
        self.next_scan_at = time.monotonic() + self.cfg.scan_interval_seconds
        if not sent:
            self._reply(chat_id, "✅ Scan done — no new directional mentions found.")
        else:
            self._reply(chat_id, f"✅ Scan done — sent {len(sent)} alert(s) above.")

    def _cmd_watchlist(self, chat_id: str, args: str) -> None:
        if not self.cfg.watchlist:
            self._reply(chat_id, "Watchlist is empty. Add one with /add.")
            return
        lines = ["*Tracked companies:*"]
        for c in sorted(self.cfg.watchlist, key=lambda x: x.get("ticker", "")):
            lines.append(f"• `{c.get('ticker','?')}` — {c.get('name','?')}")
        self._reply(chat_id, "\n".join(lines))

    def _cmd_add(self, chat_id: str, args: str) -> None:
        # Format: TICKER Name; alias1; alias2   (aliases optional)
        if not args:
            self._reply(chat_id, "Usage: /add TICKER Name; alias1; alias2", markdown=False)
            return
        head, _, alias_str = args.partition(";")
        head_parts = head.strip().split(maxsplit=1)
        ticker = head_parts[0].upper()
        name = head_parts[1].strip() if len(head_parts) > 1 else ticker
        aliases = [a.strip() for a in alias_str.split(";") if a.strip()]
        if not aliases:
            aliases = [name]

        # Replace if the ticker already exists.
        self.cfg.watchlist = [c for c in self.cfg.watchlist
                              if c.get("ticker", "").upper() != ticker]
        self.cfg.watchlist.append({"ticker": ticker, "name": name, "aliases": aliases})
        save_watchlist(self.cfg.watchlist)
        self.scanner.rebuild_matcher()
        self._reply(chat_id,
                    f"✅ Now tracking `{ticker}` — {name}\naliases: {', '.join(aliases)}")

    def _cmd_remove(self, chat_id: str, args: str) -> None:
        if not args:
            self._reply(chat_id, "Usage: /remove TICKER", markdown=False)
            return
        ticker = args.split()[0].upper()
        before = len(self.cfg.watchlist)
        self.cfg.watchlist = [c for c in self.cfg.watchlist
                              if c.get("ticker", "").upper() != ticker]
        if len(self.cfg.watchlist) == before:
            self._reply(chat_id, f"`{ticker}` was not in the watchlist.")
            return
        save_watchlist(self.cfg.watchlist)
        self.scanner.rebuild_matcher()
        self._reply(chat_id, f"🗑️ Stopped tracking `{ticker}`.")

    def _cmd_status(self, chat_id: str, args: str) -> None:
        up = utcnow() - self.started_at
        hrs, rem = divmod(int(up.total_seconds()), 3600)
        mins = rem // 60
        last = (self.scanner.last_scan_at.strftime("%Y-%m-%d %H:%M UTC")
                if self.scanner.last_scan_at else "never")
        secs_to_next = max(0, int(self.next_scan_at - time.monotonic()))
        self._reply(chat_id,
            "*Status*\n"
            f"• Uptime: {hrs}h {mins}m\n"
            f"• Scans run: {self.scanner.scan_count}\n"
            f"• Last scan: {last}\n"
            f"• Last scan alerts: {self.scanner.last_alert_count}\n"
            f"• Total alerts: {self.scanner.total_alerts}\n"
            f"• Next scan in: ~{secs_to_next // 60}m\n"
            f"• Tracking: {len(self.cfg.watchlist)} companies")

    def _cmd_sources(self, chat_id: str, args: str) -> None:
        lines = ["*Enabled sources:*"]
        for s in self.cfg.enabled_sources:
            note = ""
            if s == "truth_social" and not self.cfg.truth_social_configured:
                note = " (no credentials — inactive)"
            lines.append(f"• {s}{note}")
        self._reply(chat_id, "\n".join(lines))

    def _cmd_settings(self, chat_id: str, args: str) -> None:
        self._reply(chat_id,
            "*Settings*\n"
            f"• Scan interval: {self.cfg.scan_interval_seconds}s\n"
            f"• Lookback: {self.cfg.lookback_hours}h\n"
            f"• Notify only directional: {self.cfg.notify_only_directional}\n"
            f"• Truth Social handle: @{self.cfg.truthsocial_handle}")

    # ── main loop ───────────────────────────────────────────────────────
    def run(self) -> None:
        if not self.cfg.telegram_token:
            raise SystemExit("TELEGRAM_BOT_TOKEN is required for --serve mode.")
        log.info("interactive bot starting (scan interval %ds)", self.cfg.scan_interval_seconds)
        self._drain_backlog()
        # Announce readiness to the owner.
        if self.cfg.telegram_chat_id:
            self._reply(self.cfg.telegram_chat_id,
                        "🤖 Trump Stock Tracker is online. Send /help for commands.")

        while True:
            # 1) handle any pending commands (long-poll, so this also paces the loop)
            for update in self._poll():
                self._handle_update(update)

            # 2) run a scheduled scan if it's due
            if time.monotonic() >= self.next_scan_at:
                try:
                    self.scanner.scan_once()
                except Exception:
                    log.exception("scheduled scan failed")
                self.next_scan_at = time.monotonic() + self.cfg.scan_interval_seconds
