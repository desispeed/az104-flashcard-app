"""Play audio on Sonos via Home Assistant REST API (works remotely via Nabu Casa)."""

import os
import threading
import time
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import quote

import requests


def get_public_ip() -> str:
    """Get this machine's public IP address.

    Tries GCP metadata service first, falls back to ipify.
    """
    # Try GCP metadata server
    try:
        resp = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/"
            "network-interfaces/0/access-configs/0/external-ip",
            headers={"Metadata-Flavor": "Google"},
            timeout=2,
        )
        if resp.status_code == 200:
            return resp.text.strip()
    except requests.RequestException:
        pass

    # Fallback: external service
    resp = requests.get("https://api.ipify.org", timeout=5)
    resp.raise_for_status()
    return resp.text.strip()


class QuietHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves files without logging."""

    def log_message(self, format, *args):
        pass


def _serve_audio(directory: str, port: int) -> HTTPServer:
    """Start an HTTP server in a background thread."""
    handler = partial(QuietHandler, directory=directory)
    server = HTTPServer(("0.0.0.0", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def _ha_request(method: str, ha_url: str, ha_token: str,
                path: str, **kwargs) -> requests.Response:
    """Make an authenticated request to the Home Assistant API."""
    url = f"{ha_url.rstrip('/')}{path}"
    headers = {
        "Authorization": f"Bearer {ha_token}",
        "Content-Type": "application/json",
    }
    resp = requests.request(method, url, headers=headers, timeout=15, **kwargs)
    resp.raise_for_status()
    return resp


def list_media_players(ha_url: str, ha_token: str) -> list[dict]:
    """List all media_player entities from Home Assistant."""
    resp = _ha_request("GET", ha_url, ha_token, "/api/states")
    entities = []
    for entity in resp.json():
        eid = entity.get("entity_id", "")
        if eid.startswith("media_player."):
            attrs = entity.get("attributes", {})
            entities.append({
                "entity_id": eid,
                "name": attrs.get("friendly_name", eid),
                "state": entity.get("state", "unknown"),
            })
    return entities


def play_on_ha(audio_file_path: str, ha_url: str, ha_token: str,
               media_player_entity: str, port: int = 8765) -> None:
    """Serve an audio file and play it on Sonos via Home Assistant.

    1. Starts a temporary HTTP server on this machine's public IP
    2. Calls HA's media_player.play_media service to play the URL on Sonos
    3. Polls HA for playback state and shuts down the server when done
    """
    directory = os.path.dirname(os.path.abspath(audio_file_path))
    filename = os.path.basename(audio_file_path)

    # Start HTTP server
    server = _serve_audio(directory, port)

    try:
        # Build the public URL
        public_ip = get_public_ip()
        audio_url = f"http://{public_ip}:{port}/{quote(filename)}"
        print(f"Serving audio at: {audio_url}")

        # Tell HA to play the audio on Sonos
        _ha_request("POST", ha_url, ha_token,
                     "/api/services/media_player/play_media",
                     json={
                         "entity_id": media_player_entity,
                         "media_content_id": audio_url,
                         "media_content_type": "music",
                     })
        print(f"Playback started on {media_player_entity}")

        # Poll HA for playback state
        time.sleep(5)  # Give Sonos time to buffer
        while True:
            resp = _ha_request("GET", ha_url, ha_token,
                               f"/api/states/{media_player_entity}")
            state = resp.json().get("state", "")
            if state != "playing":
                break
            time.sleep(3)

        print("Playback finished.")

    finally:
        server.shutdown()
        print("Audio server stopped.")
