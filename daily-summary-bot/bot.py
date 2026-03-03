#!/usr/bin/env python3
"""Daily News Summary Sonos Bot.

Fetches top news headlines, converts them to speech using ElevenLabs,
and plays the audio on your Sonos speaker. Runs on a configurable daily schedule.

Usage:
    python bot.py              # Run once immediately, then schedule daily
    python bot.py --now        # Run once immediately and exit
    python bot.py --list       # List available Sonos speakers
    python bot.py --schedule   # Only run on schedule (skip immediate run)
"""

import argparse
import os
import sys
import time

import schedule
from dotenv import load_dotenv

from news_fetcher import fetch_news, build_summary_text
from tts_engine import generate_speech
from sonos_player import discover_speaker, play_on_sonos, list_speakers


def load_config() -> dict:
    """Load configuration from environment variables."""
    load_dotenv()

    config = {
        "eleven_api_key": os.getenv("ELEVEN_API_KEY"),
        "eleven_voice_id": os.getenv("ELEVEN_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb"),
        "eleven_model_id": os.getenv("ELEVEN_MODEL_ID", "eleven_multilingual_v2"),
        "brave_api_key": os.getenv("BRAVE_API_KEY"),
        "news_query": os.getenv("NEWS_QUERY", "top news today"),
        "news_max_articles": int(os.getenv("NEWS_MAX_ARTICLES", "5")),
        "sonos_speaker_name": os.getenv("SONOS_SPEAKER_NAME") or None,
        "summary_time": os.getenv("SUMMARY_TIME", "07:30"),
        "local_server_port": int(os.getenv("LOCAL_SERVER_PORT", "8765")),
    }

    if not config["eleven_api_key"]:
        print("Error: ELEVEN_API_KEY is required. Set it in your .env file.")
        sys.exit(1)

    if not config["brave_api_key"]:
        print("Error: BRAVE_API_KEY is required. Set it in your .env file.")
        sys.exit(1)

    return config


def run_summary(config: dict) -> None:
    """Execute the full pipeline: fetch news -> TTS -> play on Sonos."""
    print("\n" + "=" * 60)
    print("Starting Daily News Summary")
    print("=" * 60)

    # Step 1: Fetch news
    print("\n[1/3] Fetching today's top headlines...")
    try:
        articles = fetch_news(
            api_key=config["brave_api_key"],
            query=config["news_query"],
            count=config["news_max_articles"],
        )
    except Exception as e:
        print(f"Error fetching news: {e}")
        return

    if not articles:
        print("No articles found. Skipping summary.")
        return

    print(f"Fetched {len(articles)} articles.")
    for i, a in enumerate(articles, 1):
        print(f"  {i}. [{a['source']}] {a['title']}")

    # Step 2: Build summary and generate speech
    print("\n[2/3] Generating speech with ElevenLabs...")
    summary_text = build_summary_text(articles)
    print(f"Summary length: {len(summary_text)} characters")

    try:
        audio_path = generate_speech(
            text=summary_text,
            api_key=config["eleven_api_key"],
            voice_id=config["eleven_voice_id"],
            model_id=config["eleven_model_id"],
        )
    except Exception as e:
        print(f"Error generating speech: {e}")
        return

    # Step 3: Play on Sonos
    print("\n[3/3] Playing on Sonos...")
    try:
        speaker = discover_speaker(config["sonos_speaker_name"])
        play_on_sonos(
            audio_file_path=audio_path,
            speaker=speaker,
            port=config["local_server_port"],
        )
    except Exception as e:
        print(f"Error playing on Sonos: {e}")
        return

    print("\nDaily summary delivered successfully!")

    # Clean up temp audio file
    try:
        os.remove(audio_path)
    except OSError:
        pass


def main():
    parser = argparse.ArgumentParser(description="Daily News Summary Sonos Bot")
    parser.add_argument("--now", action="store_true",
                        help="Run once immediately and exit")
    parser.add_argument("--schedule", action="store_true",
                        help="Only run on schedule (skip immediate run)")
    parser.add_argument("--list", action="store_true",
                        help="List available Sonos speakers and exit")
    args = parser.parse_args()

    if args.list:
        print("Searching for Sonos speakers...")
        speakers = list_speakers()
        if not speakers:
            print("No Sonos speakers found on your network.")
        else:
            print(f"\nFound {len(speakers)} speaker(s):")
            for s in speakers:
                print(f"  - {s['name']} ({s['model']}) at {s['ip']}")
        return

    config = load_config()

    if args.now:
        run_summary(config)
        return

    if not args.schedule:
        # Default: run immediately, then schedule
        run_summary(config)

    # Set up scheduled daily run
    summary_time = config["summary_time"]
    print(f"\nScheduled daily summary at {summary_time}")
    print("Press Ctrl+C to stop.\n")

    schedule.every().day.at(summary_time).do(run_summary, config)

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nBot stopped.")


if __name__ == "__main__":
    main()
