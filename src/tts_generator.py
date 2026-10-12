"""Create an MP3 narration, safely splitting long scripts into smaller TTS calls."""
from pathlib import Path
import subprocess
import tempfile
import os
from uuid import uuid4

MAX_TTS_CHARS = 3000  # Deliberately below the API maximum of 4096 characters.
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"
VALID_VOICES = {"coral", "alloy", "onyx"}


def split_for_tts(text: str, max_chars: int = MAX_TTS_CHARS) -> list[str]:
    """Split at word boundaries without losing any words."""
    if max_chars <= 0 or max_chars > 4096:
        raise ValueError("max_chars must be between 1 and 4096")
    words = text.split()
    if not words:
        raise ValueError("Podcast script is empty.")
    result, current = [], []
    current_size = 0
    for word in words:
        if len(word) > max_chars:
            raise ValueError("The script contains a word too long for text-to-speech.")
        needed = len(word) + (1 if current else 0)
        if current and current_size + needed > max_chars:
            result.append(" ".join(current))
            current, current_size = [], 0
        current.append(word)
        current_size += len(word) + (1 if len(current) > 1 else 0)
    if current:
        result.append(" ".join(current))
    return result

def _speak_segment(client, segment: str, voice: str, path: Path) -> None:
    model = os.getenv("OPENAI_TTS_MODEL", "tts-1")

    params = {
        "model": model,
        "voice": voice,
        "input": segment,
        "response_format": "mp3",
    }

    # Voice instructions are supported only by GPT-based TTS models.
    if model.startswith("gpt-4o-mini-tts"):
        params["instructions"] = (
            "Speak clearly and naturally as a warm educational podcast host."
        )

    with client.audio.speech.with_streaming_response.create(
        **params
    ) as response:
        response.stream_to_file(path)

def generate_audio(script: str, voice: str = "coral", output_dir: str | Path = DEFAULT_OUTPUT_DIR, client=None) -> str:
    """Return a unique MP3 path. FFmpeg joins segments when necessary."""
    if voice not in VALID_VOICES:
        raise ValueError("Unsupported voice.")
    segments = split_for_tts(script)
    if client is None:
        from openai import OpenAI
        client = OpenAI(timeout=120.0, max_retries=2)
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"podcast_{uuid4().hex[:12]}.mp3"

    if len(segments) == 1:
        _speak_segment(client, segments[0], voice, output_path)
        return str(output_path)

    # imageio-ffmpeg supplies FFmpeg even on Windows, avoiding a manual install.
    from imageio_ffmpeg import get_ffmpeg_exe
    with tempfile.TemporaryDirectory(prefix="podcast_parts_") as temp_dir:
        temp_dir = Path(temp_dir)
        playlist = []
        for idx, segment in enumerate(segments, 1):
            path = temp_dir / f"part_{idx:03}.mp3"
            _speak_segment(client, segment, voice, path)
            playlist.append(f"file '{path.name}'")
        list_file = temp_dir / "concat.txt"
        list_file.write_text("\n".join(playlist) + "\n", encoding="utf-8")
        cmd = [get_ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
               "-f", "concat", "-safe", "0", "-i", str(list_file),
               "-c:a", "libmp3lame", "-q:a", "4", str(output_path)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except (subprocess.CalledProcessError, OSError) as exc:
            output_path.unlink(missing_ok=True)
            raise RuntimeError("Failed to combine the audio segments into an MP3.") from exc
    return str(output_path)
