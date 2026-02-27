"""Play audio files on Sonos speakers using SoCo with a local HTTP server."""

import os
import socket
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from functools import partial

import soco


def get_local_ip() -> str:
    """Get the local IP address of this machine on the LAN."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't actually send data - just determines the local IP
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


def discover_speaker(speaker_name: str | None = None) -> soco.SoCo:
    """Find a Sonos speaker on the network.

    If speaker_name is provided, finds that specific speaker.
    Otherwise returns the first speaker found.
    """
    print("Discovering Sonos speakers on your network...")
    speakers = soco.discover(timeout=10)

    if not speakers:
        raise RuntimeError(
            "No Sonos speakers found on the network. "
            "Make sure your computer is on the same network as your Sonos."
        )

    if speaker_name:
        for speaker in speakers:
            if speaker.player_name.lower() == speaker_name.lower():
                print(f"Found speaker: {speaker.player_name} ({speaker.ip_address})")
                return speaker
        available = ", ".join(s.player_name for s in speakers)
        raise RuntimeError(
            f"Speaker '{speaker_name}' not found. Available speakers: {available}"
        )

    speaker = next(iter(speakers))
    print(f"Using speaker: {speaker.player_name} ({speaker.ip_address})")
    return speaker


def list_speakers() -> list[dict]:
    """List all Sonos speakers on the network."""
    speakers = soco.discover(timeout=10)
    if not speakers:
        return []
    return [
        {"name": s.player_name, "ip": s.ip_address, "model": s.speaker_info.get("model_name", "Unknown")}
        for s in speakers
    ]


class AudioFileHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves a single audio file."""

    def __init__(self, audio_file_path: str, *args, **kwargs):
        self.audio_file_path = audio_file_path
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Serve the audio file for any GET request."""
        if not os.path.exists(self.audio_file_path):
            self.send_error(404, "Audio file not found")
            return

        file_size = os.path.getsize(self.audio_file_path)
        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.send_header("Content-Length", str(file_size))
        self.end_headers()

        with open(self.audio_file_path, "rb") as f:
            self.wfile.write(f.read())

    def log_message(self, format, *args):
        """Suppress default request logging."""
        pass


def play_on_sonos(audio_file_path: str, speaker: soco.SoCo,
                  port: int = 8765) -> None:
    """Serve an audio file via HTTP and play it on a Sonos speaker.

    Sonos can't play local files directly - it needs an HTTP URL.
    This starts a temporary HTTP server, tells the Sonos to play from it,
    and shuts down the server after playback completes.
    """
    local_ip = get_local_ip()

    handler = partial(AudioFileHandler, audio_file_path)
    server = HTTPServer(("0.0.0.0", port), handler)

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    audio_url = f"http://{local_ip}:{port}/summary.mp3"
    print(f"Serving audio at: {audio_url}")
    print(f"Playing on: {speaker.player_name}")

    try:
        speaker.play_uri(audio_url, title="Daily News Summary")
    finally:
        # Give Sonos time to fetch the file before shutting down server
        import time
        time.sleep(5)
        server.shutdown()
        print("Playback started on Sonos.")
