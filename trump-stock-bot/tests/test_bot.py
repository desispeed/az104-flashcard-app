"""Tests for the interactive command handler (no network, no file writes)."""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import src.bot as botmod  # noqa: E402
from src.bot import TelegramBot  # noqa: E402
from src.config import load_config  # noqa: E402
from src.scanner import Scanner  # noqa: E402
from src.storage import SeenStore  # noqa: E402


class FakeNotifier:
    def __init__(self):
        self.sent = []  # list of (chat_id, text)

    def send(self, text, chat_id=None, markdown=True):
        self.sent.append((chat_id, text))
        return True

    def send_signal(self, sig):
        self.sent.append((None, f"SIGNAL {sig.ticker}"))
        return True


def _make_bot(monkeypatch_saves=True):
    cfg = load_config()
    cfg.telegram_token = "test-token"
    cfg.telegram_chat_id = "555"
    # work on a copy so tests never mutate the real watchlist in memory weirdly
    cfg.watchlist = [dict(c) for c in cfg.watchlist]
    notifier = FakeNotifier()
    store = SeenStore(Path(tempfile.mkdtemp()) / "seen.db")
    scanner = Scanner(cfg, notifier=notifier, store=store)
    bot = TelegramBot(cfg, scanner=scanner)
    # never touch the real watchlist.json from tests
    botmod.save_watchlist = lambda companies: None
    return bot, notifier


def _update(text, chat_id="555"):
    return {"message": {"chat": {"id": chat_id}, "text": text}}


def test_unauthorized_chat_rejected():
    bot, n = _make_bot()
    bot._handle_update(_update("/watchlist", chat_id="999"))
    assert any("Not authorized" in t for _, t in n.sent)


def test_help_lists_commands():
    bot, n = _make_bot()
    bot._handle_update(_update("/help"))
    assert any("/scan" in t and "/add" in t for _, t in n.sent)


def test_add_then_remove_company():
    bot, n = _make_bot()
    bot._handle_update(_update("/add ZZZ Zylo Corp; Zylo; Zylo Corporation"))
    tickers = {c["ticker"] for c in bot.cfg.watchlist}
    assert "ZZZ" in tickers
    zylo = next(c for c in bot.cfg.watchlist if c["ticker"] == "ZZZ")
    assert "Zylo" in zylo["aliases"]

    bot._handle_update(_update("/remove ZZZ"))
    tickers = {c["ticker"] for c in bot.cfg.watchlist}
    assert "ZZZ" not in tickers


def test_add_rebuilds_matcher():
    bot, n = _make_bot()
    bot._handle_update(_update("/add WXYZ Widgets Inc; SuperWidget"))
    # The new alias should now be detectable by the live matcher.
    from src.models import Mention
    from datetime import datetime, timezone
    m = Mention("test", "t", "Trump loves the great SuperWidget deal", "u",
                datetime.now(timezone.utc), "1")
    sigs = bot.scanner.matcher.analyze(m)
    assert any(s.ticker == "WXYZ" for s in sigs)


def test_unknown_command():
    bot, n = _make_bot()
    bot._handle_update(_update("/frobnicate"))
    assert any("Unknown command" in t for _, t in n.sent)


def test_status_runs():
    bot, n = _make_bot()
    bot._handle_update(_update("/status"))
    assert any("Status" in t for _, t in n.sent)


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
