"""Generate speech audio from text using the ElevenLabs API."""

import os
import tempfile

from elevenlabs.client import ElevenLabs


def generate_speech(text: str, api_key: str, voice_id: str,
                    model_id: str = "eleven_multilingual_v2",
                    output_path: str | None = None) -> str:
    """Convert text to speech using ElevenLabs and save to an MP3 file.

    Returns the path to the generated audio file.
    """
    client = ElevenLabs(api_key=api_key)

    audio_generator = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        output_format="mp3_44100_128",
    )

    # Determine output path
    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=".mp3", prefix="daily_summary_")
        os.close(fd)

    # Write the audio data
    with open(output_path, "wb") as f:
        for chunk in audio_generator:
            f.write(chunk)

    file_size = os.path.getsize(output_path)
    print(f"Audio generated: {output_path} ({file_size / 1024:.1f} KB)")

    return output_path
