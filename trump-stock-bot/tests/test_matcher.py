"""Unit tests for the rule-based matcher (no network)."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.matcher import Matcher  # noqa: E402
from src.models import Mention  # noqa: E402


def _load():
    wl = json.loads((ROOT / "config" / "watchlist.json").read_text())["companies"]
    kw = json.loads((ROOT / "config" / "keywords.json").read_text())
    return Matcher(wl, kw["bullish"], kw["bearish"])


def _mention(text):
    return Mention(
        source="test", title=text, text=text, url="http://x",
        published=datetime.now(timezone.utc), raw_id=text,
    )


def test_bearish_tariff_on_apple_is_down():
    m = _load().analyze(_mention("Trump threatens 25% tariff on Apple iPhone imports"))
    apple = [s for s in m if s.ticker == "AAPL"]
    assert apple, "Apple should be detected"
    assert apple[0].direction == "DOWN"


def test_bullish_praise_on_tesla_is_up():
    m = _load().analyze(_mention("Trump praises Tesla, calls Elon Musk's work tremendous and great"))
    tsla = [s for s in m if s.ticker == "TSLA"]
    assert tsla
    assert tsla[0].direction == "UP"


def test_no_company_no_signal():
    assert _load().analyze(_mention("Trump talks about the weather today")) == []


def test_alias_word_boundary_no_false_positive():
    # "ban" stem must not fire on "urban"; "GM" must not fire inside words.
    sigs = _load().analyze(_mention("An urban development update from the administration"))
    assert sigs == []


def test_uncertain_when_balanced_or_neutral():
    m = _load().analyze(_mention("Trump mentioned Boeing in a speech"))
    boeing = [s for s in m if s.ticker == "BA"]
    assert boeing
    assert boeing[0].direction == "UNCERTAIN"


def test_multiple_companies_detected():
    text = "Trump says Apple and Boeing both got a great new deal"
    tickers = {s.ticker for s in _load().analyze(_mention(text))}
    assert {"AAPL", "BA"}.issubset(tickers)


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
