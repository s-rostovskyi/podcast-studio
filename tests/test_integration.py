"""Exercise the whole Gradio callback without spending API credits."""
from pathlib import Path
from src import main


def test_full_callback_with_fake_cloud_services(monkeypatch, tmp_path):
    fake_audio = tmp_path / "recap.mp3"
    fake_audio.write_bytes(b"mock-audio")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-never-sent")
    monkeypatch.setattr(main, "create_script", lambda text, duration_minutes: "Short recap of " + text)
    monkeypatch.setattr(main, "generate_audio", lambda script, voice: str(fake_audio))
    script, audio, download = main.make_recap(None, "Important concept", 3, "coral")
    assert script == "Short recap of Important concept"
    assert audio == download == str(fake_audio)
    assert Path(audio).is_file()
