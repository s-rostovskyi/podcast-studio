# Podcast Studio - Daily Lesson Recapper

**Team:** two contributors.  **Status:** educational MVP.

Turn pasted notes, UTF-8 TXT/MD and text-based PDFs into a 3- or 5-minute educational audio recap.
Gradio shows the generated script, an audio player and an MP3 download link.
The voice is **AI-generated**.

## Pipeline

```text
PDF/TXT/MD or pasted text
       ↓
src/data_processor.py  -> read + clean
       ↓
src/llm_processor.py   -> OpenAI Responses API; optional map/reduce chunking
       ↓
src/tts_generator.py   -> OpenAI Text-to-Speech; MP3 + FFmpeg concatenation
       ↓
src/main.py           -> Gradio UI
       ↓
Script + audio playback + downloaded .mp3
```

## Local setup (Windows PowerShell)

Install Python 3.11, Git, and VS Code first.

```powershell
git clone https://github.com/s-rostovskyi/podcast-studio.git
cd podcast-studio
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
notepad .env
python -m pytest -q
python app.py
```

## Local setup (macOS)

Install Python 3.11 and Git first.

```bash
git clone https://github.com/s-rostovskyi/podcast-studio.git
cd podcast-studio

python3.11 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

cp .env.example .env
```

Open `.env` in VS Code and configure your own
OpenAI API key and model settings.

Run the tests:

```bash
python -m pytest -q
```

Start Podcast Studio:

```bash
python app.py
```

Open http://127.0.0.1:7860 in your browser.

To stop the application, press Control+C
in the terminal.

Replace `sk-your-own-api-key-here` with your OpenAI API key (from https://platform.openai.com/api-keys).
Never commit `.env`. Open `http://127.0.0.1:7860` and use `examples/lesson_notes.txt`.

If the PowerShell virtual environment activation is blocked, run the commands with
`\.venv\Scripts\python.exe` instead (e.g. `.\.venv\Scripts\python.exe app.py`).

## Where to work

- Contributor A: `src/data_processor.py`, `src/main.py`, `app.py`, README and deployment.
- Contributor B: `src/llm_processor.py`, `src/tts_generator.py` and corresponding unit tests.
- Use separate branches and PRs; do not directly edit `main` after the initial skeleton.

## Render deployment

1. Sign in to https://dashboard.render.com/ and connect the GitHub repository.
2. Create **New → Web Service**, select repository and the Free plan if available.
3. **Runtime:** Python. **Build command:** `pip install -r requirements.txt`.
4. **Start command:** `python app.py`.
5. Configure environment variables: `OPENAI_API_KEY`, `OPENAI_LLM_MODEL`=`gpt-4o-mini`,
   `GRADIO_AUTH_USER` and `GRADIO_AUTH_PASSWORD` (recommended for public demo).
6. Deploy. Render sets `PORT`; `app.py` binds to `0.0.0.0:$PORT` automatically.
7. Open your `https://...onrender.com` URL and test with the example notes.
8. Future merges to the linked `main` branch can automatically redeploy.

Free Render web services sleep when idle and generated files are not permanent.
OpenAI API calls are billed separately. Use a restricted API key, low budget limits, and a login for a public app.

## Testing

```powershell
python -m pytest -q
```

Tests fake the API calls and **do not generate real speech**. Run a real end-to-end test
with a valid API key (upload the sample and download/play the MP3) before submission.

## How to Use

1. Open the Podcast Studio web application.
2. Upload a PDF, TXT or MD document, paste lesson notes, or provide both.
3. Select the desired podcast duration (3 or 5 minutes).
4. Choose an AI voice: coral, alloy or onyx.
5. Click "Generate podcast".
6. Review the generated podcast script.
7. Listen to the audio using the integrated player.
8. Download the generated MP3 file.

The application can summarize different educational topics without changing the Python code. All generated narration is AI-produced.

## Project Results

The application was successfully tested on Windows and macOS.

**Validation**
- 10 automated tests passed using pytest.
- Real OpenAI LLM integration was verified.
- Real text-to-speech generation was verified.
- The Gradio interface was tested locally.
- Generated MP3 files were successfully played and downloaded.

**Challenges Solved**
- Resolved an OpenAI model access error by
  switching to the supported tts-1 model.
- Configured secure environment variables
  for different development environments.
- Integrated independently developed modules
  using GitHub branches and Pull Requests.

**Future Improvements**
- Exam Preparation Mode with review questions.
- More customizable podcast formats.
- Improved progress feedback during generation.
- Permanent cloud deployment and access control.`

## Known limitations

- PDF text extraction works for selectable-text documents only; scanned PDF needs OCR.
- API key and available funds are required for real LLM and audio generation.
- Podcast duration is approximate, not guaranteed to be exactly 3/5 minutes.
- Long sources trigger extra LLM requests; long scripts trigger extra TTS requests.
- Local output MP3s are ignored by Git; cloud output files can disappear after restarts.
- For a real public product, add user accounts, request quotas, abuse protection, privacy and retention controls.
- OpenAI announced deprecation of `gpt-4o-mini-tts` model family with a future removal date: migrate the TTS implementation when necessary.

## Project assets

`examples/lesson_notes.txt` — test input; `outputs/` — generated audio directory; `.env.example` — safe configuration template.
