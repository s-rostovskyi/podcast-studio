from pathlib import Path
from src.tts_generator import split_for_tts, generate_audio

class DummySpeechResponse:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    def stream_to_file(self, path):
        Path(path).write_bytes(b"FAKE-MP3-FOR-UNIT-TEST")

class DummySpeechStream:
    def create(self, **kwargs):
        assert len(kwargs["input"]) <= 3000
        return DummySpeechResponse()

class DummyTTSClient:
    def __init__(self):
        class Container:
            pass
        self.audio = Container()
        self.audio.speech = Container()
        self.audio.speech.with_streaming_response = DummySpeechStream()


def test_tts_chunking_preserves_words():
    text = "Hello everyone. Here is a longer sentence about AI and learning."
    chunks = split_for_tts(text, 20)
    assert " ".join(chunks) == text
    assert all(len(chunk) <= 20 for chunk in chunks)


def test_single_mp3_written_with_fake_client(tmp_path):
    path = Path(generate_audio("Hello students!", output_dir=tmp_path, client=DummyTTSClient()))
    assert path.exists() and path.suffix == ".mp3"
    assert path.read_bytes() == b"FAKE-MP3-FOR-UNIT-TEST"
