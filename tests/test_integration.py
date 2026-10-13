"""Exercise the whole Gradio callback without spending API credits."""
from pathlib import Path
from src import main


def test_full_callback_with_fake_cloud_services(monkeypatch, tmp_path):
    fake_audio = tmp_path / "recap.mp3"
    fake_audio.write_bytes(b"mock-audio")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-never-sent")
    monkeypatch.setattr(main, "create_script", lambda text, duration_minutes, mode="recap": "Short recap of " + text)
    monkeypatch.setattr(main, "generate_audio", lambda script, voice: str(fake_audio))
    script, audio, download = main.make_recap(None, "Important concept", 3, "coral")
    assert script == "Short recap of Important concept"
    assert audio == download == str(fake_audio)
    assert Path(audio).is_file()

def test_progress_updates(monkeypatch, tmp_path):
    """Ensure every main processing stage reports progress."""
    import src.main as main

    fake_audio = tmp_path / "test.mp3"
    fake_audio.write_bytes(b"mock-audio")

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    monkeypatch.setattr(
        main,
        "create_script",
        lambda text, duration_minutes, mode="recap": "Test podcast script",
    )

    monkeypatch.setattr(
        main,
        "generate_audio",
        lambda script, voice: str(fake_audio),
    )

    stages = []

    def fake_progress(value, desc=None):
        stages.append(desc)

    main.make_recap(
        None,
        "Example lesson notes",
        3,
        "coral",
        mode="recap",
        progress=fake_progress,
    )

    assert stages == [
        "Processing lesson notes...",
        "Generating podcast script...",
        "Creating MP3 audio...",
        "Podcast ready!",
    ]


def test_missing_api_key_shows_clear_error(monkeypatch):
    """Missing API credentials must produce a user-friendly error."""
    import gradio as gr
    import pytest
    import src.main as main

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(gr.Error, match="OpenAI API key"):
        main.make_recap(
            None,
            "Example lesson notes",
            3,
            "coral",
        )