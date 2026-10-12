"""Read PDF/TXT/MD input, clean it and prepare a podcast source."""
from pathlib import Path
import re
from pypdf import PdfReader

MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MiB
MAX_TEXT_CHARS = 250_000
SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}

def read_transcript(file_path: str | Path) -> str:
    """Return extracted text; scanned image-only PDF files need OCR separately."""
    path = Path(file_path)
    if not path.is_file():
        raise ValueError("Uploaded file was not found.")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError("Please upload a PDF, TXT or MD file.")
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("File is too large (maximum: 10 MB).")

    if path.suffix.lower() == ".pdf":
        try:
            reader = PdfReader(str(path))
            text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            raise ValueError("Unable to read this PDF. Check if it is encrypted or damaged.") from exc
    else:
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeError as exc:
            raise ValueError("Please save the text file as UTF-8 and upload it again.") from exc
    if not text.strip():
        raise ValueError("The file contains no readable text. Scanned PDFs need OCR.")
    return text

def clean_text(text: str) -> str:
    """Remove timestamp prefixes, English filler words and excess whitespace."""
    text = re.sub(r"(?m)^\s*\[?\d{1,2}:\d{2}(?::\d{2})?\]?\s*", "", text)
    text = re.sub(r"\b(?:um|uh)\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"(?m)^ +", "", text)
    text = re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", text)
    return text.strip()

def prepare_input(notes: str | None, file_path: str | None) -> str:
    """Combine pasted notes and uploaded file when both are supplied."""
    parts = []
    if file_path:
        parts.append(read_transcript(file_path))
    if notes and notes.strip():
        parts.append(notes.strip())
    cleaned = clean_text("\n\n".join(parts))
    if not cleaned:
        raise ValueError("Please paste some notes or upload a PDF/TXT/MD file.")
    if len(cleaned) > MAX_TEXT_CHARS:
        raise ValueError("Input too long: keep it below 250,000 characters.")
    return cleaned
