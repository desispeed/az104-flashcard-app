#!/usr/bin/env python3
"""Trump stock-mention tracker — CLI entrypoint.

Examples:
    python main.py --once            # run a single scan and exit
    python main.py --loop            # scan forever, every SCAN_INTERVAL_SECONDS
    python main.py --test-telegram   # send a test message to your chat
    python main.py --chat-id         # print chat ids that have messaged the bot
"""
from __future__ import annotations

import argparse
import logging
import sys
import time

from src.config import load_config
from src.scanner import Scanner


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def cmd_chat_id(cfg) -> int:
    """Print chat ids of anyone who has messaged the bot (helper for setup)."""
    import requests
    if not cfg.telegram_token:
        print("TELEGRAM_BOT_TOKEN is not set in your .env", file=sys.stderr)
        return 1
    try:
        resp = requests.get(
            f"https://api.telegram.org/bot{cfg.telegram_token}/getUpdates",
            timeout=20,
        )
    except requests.RequestException as exc:
        print(f"Could not reach Telegram (network?): {exc}", file=sys.stderr)
        return 1
    try:
        data = resp.json()
    except ValueError:
        print(f"Telegram returned a non-JSON response (status {resp.status_code}). "
              f"Likely blocked egress or a bad token.", file=sys.stderr)
        return 1
    if not data.get("ok"):
        print(f"Telegram error: {data}", file=sys.stderr)
        return 1
    found = {}
    for upd in data.get("result", []):
        msg = upd.get("message") or upd.get("channel_post") or {}
        chat = msg.get("chat") or {}
        if chat.get("id") is not None:
            found[chat["id"]] = chat.get("username") or chat.get("title") or chat.get("first_name", "")
    if not found:
        print("No messages yet. Open Telegram, send your bot any message, then re-run.")
        return 0
    print("Chat ids that have messaged this bot:")
    for cid, who in found.items():
        print(f"  {cid}   ({who})")
    print("\nPut the right id in TELEGRAM_CHAT_ID in your .env")
    return 0


def cmd_test_telegram(cfg) -> int:
    from src.notifier import TelegramNotifier
    n = TelegramNotifier(cfg.telegram_token, cfg.telegram_chat_id)
    ok = n.send("✅ Trump stock-tracker bot is connected and working.")
    print("Sent." if ok else "Failed — check token/chat id (see logs).")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Trump stock-mention tracker bot")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--once", action="store_true", help="run one scan and exit")
    group.add_argument("--loop", action="store_true", help="scan repeatedly on an interval")
    group.add_argument("--test-telegram", action="store_true", help="send a test Telegram message")
    group.add_argument("--chat-id", action="store_true", help="list chat ids that messaged the bot")
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    args = parser.parse_args()

    _setup_logging(args.verbose)
    cfg = load_config()

    if args.chat_id:
        return cmd_chat_id(cfg)
    if args.test_telegram:
        return cmd_test_telegram(cfg)

    scanner = Scanner(cfg)

    if args.once:
        scanner.scan_once()
        return 0

    # --loop
    log = logging.getLogger("main")
    interval = cfg.scan_interval_seconds
    log.info("starting loop; scanning every %ds (sources: %s)",
             interval, ", ".join(cfg.enabled_sources))
    while True:
        try:
            scanner.scan_once()
        except Exception as exc:
            log.exception("scan failed: %s", exc)
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
