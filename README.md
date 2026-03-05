# Daily News Summary Sonos Bot

A Python bot that fetches your daily news headlines via **Brave Search**, converts them to natural speech using **ElevenLabs** text-to-speech, and plays the audio on your **Sonos** speaker every morning — controlled remotely through **Home Assistant**.

## How It Works

1. **Fetches news** - Pulls top headlines from [Brave Search API](https://brave.com/search/api/)
2. **Generates speech** - Converts the summary to audio via [ElevenLabs](https://elevenlabs.io) TTS
3. **Plays on Sonos** - Serves the audio file over HTTP and tells Sonos to play it via [Home Assistant](https://www.home-assistant.io/) (or directly via LAN)

## Prerequisites

- An [ElevenLabs API key](https://elevenlabs.io) (free tier available)
- A [Brave Search API key](https://brave.com/search/api/) (free tier available)
- A [Home Assistant](https://www.home-assistant.io/) instance with [Nabu Casa](https://www.nabucasa.com/) (for remote control from GCP)
- A Sonos speaker integrated with Home Assistant
- Docker and Docker Compose

## Quick Start (Docker on GCP)

```bash
cd daily-summary-bot

# Create your .env from the template
cp .env.example .env

# Edit .env — add your API keys and HA settings
nano .env

# Find your Sonos media_player entity ID
python bot.py --list
# Copy the entity_id (e.g. media_player.living_room) into .env

# Build and run
docker compose up -d

# Test immediately
docker compose run --rm daily-summary-bot --now

# View logs
docker compose logs -f
```

## Usage

```bash
# Run once now and then schedule daily
python bot.py

# Run once immediately and exit
python bot.py --now

# Only run on schedule (no immediate run)
python bot.py --schedule

# List available speakers (HA entities or LAN Sonos devices)
python bot.py --list
```

## Configuration

All settings are in the `.env` file:

### API Keys

| Variable | Default | Description |
|---|---|---|
| `ELEVEN_API_KEY` | *required* | Your ElevenLabs API key |
| `ELEVEN_VOICE_ID` | `JBFqnCBsd6RMkjVDRZzb` | Voice to use (George by default) |
| `ELEVEN_MODEL_ID` | `eleven_multilingual_v2` | TTS model |
| `BRAVE_API_KEY` | *required* | Your Brave Search API key |
| `NEWS_QUERY` | `top news today` | Search query for news headlines |
| `NEWS_MAX_ARTICLES` | `5` | Number of articles in each summary |

### Home Assistant (recommended for GCP)

| Variable | Default | Description |
|---|---|---|
| `HA_URL` | *(none)* | Your Nabu Casa URL (e.g. `https://xxx.ui.nabu.casa`) |
| `HA_TOKEN` | *(none)* | Long-lived access token from HA |
| `HA_MEDIA_PLAYER` | *(none)* | Sonos entity ID (e.g. `media_player.living_room`) |

When all three `HA_*` variables are set, the bot plays audio through Home Assistant. Otherwise it falls back to direct Sonos control via SoCo (requires same LAN).

### Other Settings

| Variable | Default | Description |
|---|---|---|
| `SONOS_SPEAKER_NAME` | *(auto-discover)* | Direct Sonos fallback — speaker name from Sonos app |
| `SUMMARY_TIME` | `07:30` | Daily delivery time (24h format) |
| `LOCAL_SERVER_PORT` | `8765` | Port for serving audio to Sonos |

## Setting Up Home Assistant

1. **Create a long-lived access token** in HA: Profile → Security → Long-Lived Access Tokens → Create Token

2. **Find your Sonos entity ID**: run `python bot.py --list` with `HA_URL` and `HA_TOKEN` set, or check HA → Settings → Devices → Sonos

3. **Open the audio port** on your GCP VM firewall so your Sonos speaker can fetch the audio:
   ```bash
   gcloud compute firewall-rules create allow-audio-server \
     --allow tcp:8765 \
     --target-tags=your-vm-tag \
     --description="Allow Sonos to fetch audio from news bot"
   ```

## Deploying on GCP VM

```bash
# SSH into your VM
gcloud compute ssh your-vm-name

# Clone the repo
git clone <your-repo-url>
cd az104-flashcard-app/daily-summary-bot

# Set up your .env
cp .env.example .env
nano .env

# Open the audio serving port in GCP firewall
gcloud compute firewall-rules create allow-audio-server \
  --allow tcp:8765

# Start with Docker Compose
docker compose up -d

# Verify it's running
docker compose logs -f
```

## Architecture

```
daily-summary-bot/
├── bot.py             # Main entry point and scheduler
├── news_fetcher.py    # Brave Search API integration
├── tts_engine.py      # ElevenLabs TTS integration
├── ha_player.py       # Home Assistant playback (remote Sonos control)
├── sonos_player.py    # Direct Sonos playback (LAN fallback)
├── requirements.txt   # Python dependencies
├── Dockerfile         # Container image definition
├── docker-compose.yml # Container orchestration
├── .dockerignore      # Files excluded from Docker build
├── .env.example       # Configuration template
└── .env               # Your configuration (not committed)
```

```
[Cron/Scheduler] → [Brave Search] → [Build Summary]
                                          ↓
                                   [ElevenLabs TTS]
                                          ↓
                                     [Save MP3]
                                          ↓
                              [Serve via HTTP on public IP]
                                          ↓
                          [HA API: media_player.play_media]
                                          ↓
                                  [Sonos plays audio]
```

## Troubleshooting

- **"No media_player entities found"** — Make sure your Sonos is integrated in HA (Settings → Integrations → Sonos).
- **Audio doesn't play from GCP** — Ensure port 8765 is open in your GCP firewall and the VM has a public IP. The Sonos speaker fetches audio directly from your VM.
- **HA API errors** — Verify your long-lived access token hasn't expired. Regenerate from HA Profile → Security.
- **ElevenLabs errors** — Check your API key and remaining credits at [elevenlabs.io](https://elevenlabs.io).
- **Fallback to direct Sonos** — If `HA_URL` is not set, the bot uses SoCo for direct LAN control. This only works if the bot runs on the same network as your Sonos.
