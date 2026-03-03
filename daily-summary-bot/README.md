# Daily News Summary Sonos Bot

A Python bot that fetches your daily news headlines via **Brave Search**, converts them to natural speech using **ElevenLabs** text-to-speech, and plays the audio on your **Sonos** speaker every morning.

## How It Works

1. **Fetches news** - Pulls top headlines from [Brave Search API](https://brave.com/search/api/) based on your search query
2. **Generates speech** - Sends the summary text to [ElevenLabs](https://elevenlabs.io) TTS API and gets back natural-sounding audio
3. **Plays on Sonos** - Spins up a temporary local HTTP server, serves the audio file, and tells your Sonos speaker to play it via [SoCo](https://github.com/SoCo/SoCo)

## Prerequisites

- A Sonos speaker on the same local network
- An [ElevenLabs API key](https://elevenlabs.io) (free tier available)
- A [Brave Search API key](https://brave.com/search/api/) (free tier available)
- Docker and Docker Compose (for containerized deployment)

## Quick Start (Docker)

```bash
cd daily-summary-bot

# Create your .env from the template and add your API keys
cp .env.example .env
# Edit .env with your keys

# Build and run
docker compose up -d

# Test immediately
docker compose run --rm daily-summary-bot --now

# View logs
docker compose logs -f
```

## Quick Start (Local)

```bash
cd daily-summary-bot

# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create your .env file
cp .env.example .env
# Edit .env with your keys

# Test it
python bot.py --now
```

## Usage

```bash
# Run once now and then schedule daily
python bot.py

# Run once immediately and exit
python bot.py --now

# Only run on schedule (no immediate run)
python bot.py --schedule

# List all Sonos speakers on your network
python bot.py --list
```

## Configuration

All settings are in the `.env` file:

| Variable | Default | Description |
|---|---|---|
| `ELEVEN_API_KEY` | *required* | Your ElevenLabs API key |
| `ELEVEN_VOICE_ID` | `JBFqnCBsd6RMkjVDRZzb` | Voice to use (George by default) |
| `ELEVEN_MODEL_ID` | `eleven_multilingual_v2` | TTS model (`eleven_v3`, `eleven_flash_v2_5`, etc.) |
| `BRAVE_API_KEY` | *required* | Your Brave Search API key |
| `NEWS_QUERY` | `top news today` | Search query for news headlines |
| `NEWS_MAX_ARTICLES` | `5` | Number of articles in each summary |
| `SONOS_SPEAKER_NAME` | *(auto-discover)* | Target speaker name (from Sonos app) |
| `SUMMARY_TIME` | `07:30` | Daily delivery time (24h format) |
| `LOCAL_SERVER_PORT` | `8765` | Port for the temporary audio server |

### Choosing a Voice

Browse voices at the [ElevenLabs Voice Library](https://elevenlabs.io/voice-library). Copy the voice ID and set `ELEVEN_VOICE_ID` in your `.env`.

## Deploying on GCP VM

```bash
# SSH into your VM
gcloud compute ssh your-vm-name

# Clone the repo and cd into the bot directory
git clone <your-repo-url>
cd az104-flashcard-app/daily-summary-bot

# Set up your .env
cp .env.example .env
nano .env  # Add your API keys

# Start with Docker Compose
docker compose up -d

# Verify it's running
docker compose logs -f
```

The container uses `network_mode: host` so it can discover Sonos speakers via SSDP multicast on your local network. It restarts automatically unless explicitly stopped.

## Architecture

```
daily-summary-bot/
├── bot.py             # Main entry point and scheduler
├── news_fetcher.py    # Brave Search API integration
├── tts_engine.py      # ElevenLabs TTS integration
├── sonos_player.py    # Sonos discovery, HTTP server, and playback
├── requirements.txt   # Python dependencies
├── Dockerfile         # Container image definition
├── docker-compose.yml # Container orchestration
├── .dockerignore      # Files excluded from Docker build
├── .env.example       # Configuration template
└── .env               # Your configuration (not committed)
```

## Troubleshooting

- **"No Sonos speakers found"** - Make sure your VM/computer and Sonos are on the same WiFi/LAN. Some networks isolate devices.
- **"Speaker 'X' not found"** - Run `python bot.py --list` to see available speaker names. The name must match exactly.
- **ElevenLabs errors** - Check your API key and that you have remaining credits at [elevenlabs.io](https://elevenlabs.io).
- **Audio doesn't play** - Ensure port 8765 (or your configured port) isn't blocked by a firewall. The Sonos needs to reach your computer's IP on that port.
- **Docker networking** - The container uses `network_mode: host` which is required for Sonos discovery. This only works on Linux hosts (which GCP VMs are).
