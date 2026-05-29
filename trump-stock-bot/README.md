# Trump Stock-Mention Tracker Bot

Scans news + Trump's Truth Social posts on a schedule, detects which public
companies are being talked about, and pushes a Telegram alert with a rough
**up / down** lean based on the language used.

> ⚠️ **Not financial advice.** This is a rule-based keyword heuristic, not a
> prediction model. It tells you *that* Trump/news mentioned a company and
> whether the wording sounds positive or negative — nothing more. Do your own
> research before trading.

---

## How it works

```
 sources/                matcher                 notifier
 ┌───────────────┐       ┌──────────────┐        ┌────────────┐
 │ Google News   │──┐    │ watchlist    │        │ Telegram   │
 │ GDELT         │──┼──▶ │ + bullish/   │ ─────▶ │ push msg   │
 │ Truth Social  │──┘    │ bearish kw   │        └────────────┘
 └───────────────┘       └──────────────┘
        ▲                       │
   every hour            de-dup via SQLite (data/seen.db)
```

1. **Sources** (`src/sources/`) fetch recent items:
   - `google_news` — Google News RSS, free, no key (stdlib XML parsing).
   - `gdelt` — GDELT 2.0 DOC API, free, no key (headlines only).
   - `truth_social` — Trump's posts via the unofficial `truthbrush` lib
     (needs a Truth Social login; best-effort, degrades gracefully).
2. **Matcher** (`src/matcher.py`) scans each item for watchlist company
   aliases, then scores the text against weighted bullish/bearish keyword
   stems to produce `UP` / `DOWN` / `UNCERTAIN`.
3. **De-dup** (`src/storage.py`) — SQLite remembers what it already alerted on
   so you never get the same item twice.
4. **Notifier** (`src/notifier.py`) sends a formatted Telegram message.

Everything is configured by editing two JSON files and a `.env`:
- `config/watchlist.json` — companies → tickers + aliases. **Add your own.**
- `config/keywords.json` — bullish/bearish stems + weights. **Tune freely.**

---

## Quick start (local)

```bash
cd trump-stock-bot
pip install -r requirements.txt
pip install truthbrush          # optional, for Truth Social

cp .env.example .env            # then edit .env (see below)
```

Fill in `.env`:

| Variable | Required | Notes |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ | From @BotFather |
| `TELEGRAM_CHAT_ID` | ✅ | Your chat id (see below) |
| `TRUTHSOCIAL_USERNAME` / `_PASSWORD` | optional | Enables Truth Social source |
| `TRUTHSOCIAL_HANDLE` | optional | Default `realDonaldTrump` |
| `LOOKBACK_HOURS` | optional | Default `1` |
| `SCAN_INTERVAL_SECONDS` | optional | Default `3600` (1h) |
| `ENABLED_SOURCES` | optional | Default `google_news,gdelt,truth_social` |
| `NOTIFY_ONLY_DIRECTIONAL` | optional | Default `true` |

**Find your chat id:** open Telegram, send your bot any message, then:

```bash
python main.py --chat-id        # prints chat ids that messaged the bot
python main.py --test-telegram  # sends a "connected!" message
```

Run it:

```bash
python main.py --once     # single scan (good for your own cron)
python main.py --loop     # run forever, scanning every SCAN_INTERVAL_SECONDS
python main.py --loop -v  # verbose
```

For a system cron instead of `--loop`:

```cron
0 * * * * cd /path/to/trump-stock-bot && /usr/bin/python3 main.py --once >> bot.log 2>&1
```

---

## Run with Docker

```bash
docker compose up -d --build      # builds and runs in the background (--loop)
docker compose logs -f            # watch it
docker compose down               # stop
```

The `data/` dir is mounted as a volume so the de-dup DB survives restarts.
`.env` is read via `env_file` and is **never** baked into the image.

---

## Deploy to a GCP VM

A helper script provisions a small VM, installs Docker, copies the project,
and starts the container.

Prereqs on your machine: `gcloud` CLI authenticated (`gcloud auth login`) and a
project set (`gcloud config set project <PROJECT_ID>`), plus a filled-in `.env`.

```bash
./scripts/deploy_gcp.sh
# or override defaults:
VM_NAME=trump-bot ZONE=us-central1-a MACHINE_TYPE=e2-small ./scripts/deploy_gcp.sh
```

Manage it afterwards:

```bash
gcloud compute ssh trump-stock-bot --zone us-central1-a \
  --command 'cd /opt/trump-stock-bot && sudo docker compose logs -f'
```

The bot is **push-only** — no inbound ports are opened on the VM.

---

## Tuning & accuracy notes

- **Add companies** to `config/watchlist.json`. Keep aliases specific —
  generic words cause false matches.
- **Tune sentiment** in `config/keywords.json` (stems match as word prefixes,
  so `tariff` also catches `tariffs`).
- GDELT only exposes **headlines**, so its sentiment read is shallower than
  Truth Social posts (full text).
- Truth Social has **no official API**; `truthbrush` is unofficial, rate
  limited, and may break when the site changes. The bot logs and continues if
  it fails.
- The direction is a **keyword heuristic**, not a forecast. Treat alerts as
  "here's a mention worth a look," not a trade signal.

## Tests

```bash
python tests/test_matcher.py      # no network needed
```
