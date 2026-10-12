from pathlib import Path
import pytest
from src.data_processor import clean_text, read_transcript, prepare_input

def test_cleaning():
    assert clean_text("00:12 Um Machine learning  works.\n\n\nUh Next") == "Machine learning works.\n\nNext"

def test_txt_file(tmp_path: Path):
    file = tmp_path / "lesson.txt"
    file.write_text("Important lesson concept.", encoding="utf-8")
    assert read_transcript(file) == "Important lesson concept."
    assert "extra context" in prepare_input("extra context", str(file))

def test_missing_input():
    with pytest.raises(ValueError, match="Please paste"):
        prepare_input("", None)

def test_wrong_file(tmp_path: Path):
    file = tmp_path / "image.jpg"
    file.write_bytes(b"test")
    with pytest.raises(ValueError, match="PDF, TXT or MD"):
        read_transcript(file)
