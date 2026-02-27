# Daily News Summary Sonos Bot

A Python bot that fetches your daily news headlines, converts them to natural speech using **ElevenLabs** text-to-speech, and plays the audio on your **Sonos** speaker every morning.

## How It Works

1. **Fetches news** - Pulls top headlines from [NewsAPI](https://newsapi.org) based on your country/category preferences
2. **Generates speech** - Sends the summary text to [ElevenLabs](https://elevenlabs.io) TTS API and gets back natural-sounding audio
3. **Plays on Sonos** - Spins up a temporary local HTTP server, serves the audio file, and tells your Sonos speaker to play it via [SoCo](https://github.com/SoCo/SoCo)

## Prerequisites

- Python 3.10+
- A Sonos speaker on the same local network
- An [ElevenLabs API key](https://elevenlabs.io) (free tier available)
- A [NewsAPI key](https://newsapi.org/register) (free tier available)

## Setup

```bash
cd daily-summary-bot

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create your .env file from the template
cp .env.example .env
```

Edit `.env` and fill in your API keys:

```
ELEVEN_API_KEY=your_elevenlabs_key
NEWS_API_KEY=your_newsapi_key
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
| `NEWS_API_KEY` | *required* | Your NewsAPI key |
| `NEWS_COUNTRY` | `us` | Country code for headlines |
| `NEWS_CATEGORY` | `general` | Category: general, business, tech, sports, etc. |
| `NEWS_MAX_ARTICLES` | `5` | Number of articles in each summary |
| `SONOS_SPEAKER_NAME` | *(auto-discover)* | Target speaker name (from Sonos app) |
| `SUMMARY_TIME` | `07:30` | Daily delivery time (24h format) |
| `LOCAL_SERVER_PORT` | `8765` | Port for the temporary audio server |

### Choosing a Voice

Browse voices at the [ElevenLabs Voice Library](https://elevenlabs.io/voice-library). Copy the voice ID and set `ELEVEN_VOICE_ID` in your `.env`.

## Running as a System Service

To run the bot persistently so it delivers summaries every day:

### Using systemd (Linux)

```bash
sudo tee /etc/systemd/system/daily-summary-bot.service > /dev/null <<EOF
[Unit]
Description=Daily News Summary Sonos Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python bot.py --schedule
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable daily-summary-bot
sudo systemctl start daily-summary-bot
```

### Using launchd (macOS)

```bash
cat > ~/Library/LaunchAgents/com.daily-summary-bot.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.daily-summary-bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(pwd)/venv/bin/python</string>
        <string>$(pwd)/bot.py</string>
        <string>--schedule</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.daily-summary-bot.plist
```

## Architecture

```
daily-summary-bot/
├── bot.py             # Main entry point and scheduler
├── news_fetcher.py    # NewsAPI integration
├── tts_engine.py      # ElevenLabs TTS integration
├── sonos_player.py    # Sonos discovery, HTTP server, and playback
├── requirements.txt   # Python dependencies
├── .env.example       # Configuration template
└── .env               # Your configuration (not committed)
```

## Troubleshooting

- **"No Sonos speakers found"** - Make sure your computer and Sonos are on the same WiFi/LAN. Some networks isolate devices.
- **"Speaker 'X' not found"** - Run `python bot.py --list` to see available speaker names. The name must match exactly.
- **ElevenLabs errors** - Check your API key and that you have remaining credits at [elevenlabs.io](https://elevenlabs.io).
- **Audio doesn't play** - Ensure port 8765 (or your configured port) isn't blocked by a firewall. The Sonos needs to reach your computer's IP on that port.
