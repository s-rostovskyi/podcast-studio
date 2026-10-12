
# Podcast Studio – Lesson Recapper

Turn lesson notes, transcripts or PDFs into a short, AI-narrated podcast recap. Upload a file or paste text, pick a duration and voice, and get back a written script plus a downloadable MP3.

> The narration is AI-generated, not a human voice. Podcast scripts are written by an LLM using only your source text for factual claims.

## How it works

```
PDF / TXT / MD  ─┐
                 ├─► clean & combine ─► LLM script ─► text-to-speech ─► MP3
Pasted notes   ──┘   (data_processor)   (llm_processor)  (tts_generator)
```

1. **Input** – Reads a PDF, TXT or MD file and/or pasted notes. Timestamps (e.g. `[01:23]`), filler words ("um", "uh") and extra whitespace are removed.
2. **Script** – An OpenAI model writes a spoken-style script: friendly greeting, five key learning points with simple examples, and a recap. Long sources are first summarized in segments (map/reduce), then merged into one script.
3. **Audio** – The script is split into chunks that fit the TTS limit, each chunk is narrated, and FFmpeg joins them into a single MP3.
4. **UI** – A Gradio app wires it all together and shows the script, an audio player and a download link.

## Project structure

```
project-root/
├── .env                    # your API key and optional settings (not committed)
├── outputs/                # generated MP3s (created automatically)
└── src/
    ├── main.py             # Gradio interface and pipeline entry point
    ├── data_processor.py   # file reading, validation, text cleaning
    ├── llm_processor.py    # script generation (single pass or map/reduce)
    └── tts_generator.py    # text splitting, TTS calls, MP3 joining
```

`main.py` loads `.env` from the project root, and MP3s are written to `outputs/` in the project root.

## Requirements

- Python 3.10+
- An OpenAI API key with access to a chat/responses model and a text-to-speech model

Install dependencies:

```bash
pip install gradio python-dotenv pypdf openai imageio-ffmpeg
```

`imageio-ffmpeg` bundles an FFmpeg binary, so no separate FFmpeg install is needed (including on Windows).

## Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...

# Optional
OPENAI_LLM_MODEL=gpt-4o-mini
OPENAI_TTS_MODEL=tts-1
```

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | – (required) | Authenticates all OpenAI calls |
| `OPENAI_LLM_MODEL` | `gpt-4o-mini` | Model that writes the script |
| `OPENAI_TTS_MODEL` | `tts-1` | Model that narrates the script |

If you set `OPENAI_TTS_MODEL` to a `gpt-4o-mini-tts` model, the narrator is also given a style instruction (warm, clear educational host). Other TTS models ignore this.

## Running the app

Run from the project root so the `src` imports resolve:

```bash
python -m src.main
```

Note: `main.py` defines the Gradio app (`demo`) but does not launch it. Add this at the bottom of the file:

```python
if __name__ == "__main__":
    demo.launch()
```

Then open the local URL Gradio prints (usually http://127.0.0.1:7860).

## Usage

1. Upload a `.pdf`, `.txt` or `.md` file, paste notes into the text box, or do both (they are combined).
2. Choose a target duration: **3** or **5** minutes.
3. Choose a voice: `coral`, `alloy` or `onyx`.
4. Click **Generate podcast**.
5. Read the script, listen in the player, or download the MP3.

## Limits and behavior

| Item | Limit / behavior |
|---|---|
| File types | `.pdf`, `.txt`, `.md` |
| File size | 10 MB maximum |
| Total input text | 250,000 characters maximum |
| Text files | Must be UTF-8 |
| Scanned PDFs | Not supported – image-only PDFs need OCR first |
| Script length | About 125 words per minute (≈375 words for 3 min, ≈625 for 5 min) |
| Long sources | Split into ~3,500-word segments, summarized, then merged |
| TTS chunking | Scripts are split at word boundaries into ≤3,000-character pieces and joined with FFmpeg |
| Concurrency | One generation at a time (`concurrency_limit=1`) |
| Language | The script prompt produces English output |

## Cost

Every run uses your own OpenAI billing account. Long inputs trigger multiple LLM calls (one per segment plus one for the final script), and long scripts trigger multiple TTS calls.

## Safety notes

- The script prompt instructs the model to use only the supplied text for facts and to treat any instructions inside the source as untrusted content.
- Output filenames are randomized (`podcast_<id>.mp3`), so generations don't overwrite each other.
- Generated files accumulate in `outputs/`; delete them periodically.

## Troubleshooting

| Message | Likely cause |
|---|---|
| "OPENAI_API_KEY is not configured on the server." | Missing or misplaced `.env` file (it must be in the project root) |
| "The file contains no readable text. Scanned PDFs need OCR." | Image-only PDF |
| "Unable to read this PDF…" | Encrypted or damaged PDF |
| "Please save the text file as UTF-8…" | Text file uses a different encoding |
| "Podcast generation failed. Check API balance, model access and server logs." | API quota/billing, a model name you don't have access to, or a network error – see the server logs |
| "Failed to combine the audio segments into an MP3." | FFmpeg joining failed; check that `imageio-ffmpeg` is installed |

## Testing

`split_into_chunks` and `split_for_tts` are pure functions, and both `create_script` and `generate_audio` accept an optional `client` argument, so the pipeline can be tested offline with a fake client.
