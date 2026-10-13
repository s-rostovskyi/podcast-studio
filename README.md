# Podcast Studio - Daily Lesson Recapper

**Team:** Sergii Rostovskyi & Pieter Albrecht
**Project status:** Completed educational MVP  
**Tech stack:** Python · Gradio · OpenAI Responses API · OpenAI Text-to-Speech · FFmpeg · pytest

## Project Overview

Podcast Studio transforms written lesson notes into short, AI-narrated educational podcasts.

Instead of rereading lengthy transcripts, students can listen to a concise recap of a lesson or generate a podcast designed to support exam preparation.

The application accepts pasted text, TXT/MD files, and text-based PDFs. It generates a structured podcast script, converts it into speech, and provides audio playback and an MP3 download.

**All podcast narration is AI-generated, not recorded by a human.**

## Key Features

### Two Learning Modes

**Lesson Recap**
- Summarizes the main concepts from lesson notes.
- Presents the material in a clear, conversational podcast format.
- Helps learners review topics while commuting, walking, or doing other activities.

**Exam Preparation**
- Reviews important concepts from the source material.
- Includes three self-check questions with answers.
- Supports active recall and exam revision.

### Additional Features

- **Multiple input formats:** PDF, TXT, Markdown, and pasted text.
- **Customizable duration:** Approximately 3 or 5 minutes.
- **AI voice selection:** Coral, Alloy, or Onyx.
- **Readable transcript:** View the generated script before or while listening.
- **MP3 playback and download:** Listen directly in the browser or save the audio.
- **Progress indicator:** Follow the document-processing, script-generation, and audio-generation stages.
- **Error handling:** Receive understandable messages for invalid input, missing configuration, API access problems, and connectivity failures.
- **Long-document processing:** Supports chunked LLM processing and consolidation when required.

## Architecture

The application uses a modular processing pipeline.

```text
PDF / TXT / MD / Pasted Notes
              |
              v
  src/data_processor.py
   Text extraction and cleaning
              |
              v
   src/llm_processor.py
  OpenAI Responses API
  Lesson Recap / Exam Preparation
  Optional chunking and consolidation
              |
              v
   src/tts_generator.py
  OpenAI Text-to-Speech
  MP3 generation and FFmpeg concatenation
              |
              v
        src/main.py
       Gradio interface
              |
              v
  Transcript + Audio Player
        + MP3 Download
```

**Main components**

| File | Responsibility |
|---|---|
| `src/data_processor.py` | Reads and prepares text from supported input formats. |
| `src/llm_processor.py` | Generates scripts using the OpenAI Responses API and the selected learning mode. |
| `src/tts_generator.py` | Converts generated scripts into MP3 audio and combines audio chunks when necessary. |
| `src/main.py` | Provides the Gradio interface, workflow orchestration, progress reporting, and error handling. |
| `app.py` | Starts the application for local development or deployment. |
| `tests/` | Contains automated tests for the processing modules and their integration. |

## Requirements

- Python 3.11
- Git
- OpenAI API key with access to the configured models
- Active OpenAI API billing or available credits
- FFmpeg available on the system PATH for workflows requiring audio concatenation

VS Code is recommended but not required.

## Installation and Local Setup

### Windows (PowerShell)

Clone the repository:

```powershell
git clone https://github.com/s-rostovskyi/podcast-studio.git
cd podcast-studio
```

Create and activate a Python virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Create your local configuration:

```powershell
Copy-Item .env.example .env
notepad .env
```

Add your own OpenAI API key and configure the models.

If PowerShell blocks environment activation, use the virtual environment's Python directly, for example:

```powershell
.\.venv\Scripts\python.exe app.py
```

### macOS

Clone the repository:

```bash
git clone https://github.com/s-rostovskyi/podcast-studio.git
cd podcast-studio
```

Create and activate a Python environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Create your local configuration:

```bash
cp .env.example .env
```

Open `.env` in your preferred editor and configure your API key and model settings.

You can also use an existing Conda environment with Python 3.11. Make sure that VS Code and the terminal are using the same interpreter.

### Environment Configuration

The `.env.example` file provides a configuration template. Important settings include:

```dotenv
OPENAI_API_KEY=your-own-api-key
OPENAI_LLM_MODEL=gpt-4o-mini
OPENAI_TTS_MODEL=tts-1
```

The `tts-1` model was selected for this project after the team encountered an access restriction with an alternative TTS model.

Model access depends on the OpenAI account and project configuration.

**Security:** Never commit `.env` or publish your API key. Only the safe `.env.example` template should be tracked in Git.

## Running the Application

Run the automated tests:

```bash
python -m pytest -q
```

Start the application:

```bash
python app.py
```

Open the local web interface:

http://127.0.0.1:7860

To stop the application, press `Ctrl+C` in the terminal.

### How to Use

1. Open Podcast Studio in your browser.
2. Upload a PDF, TXT, or MD file, paste lesson notes, or provide both.
3. Choose **Lesson Recap** or **Exam Preparation**.
4. Select a target duration of 3 or 5 minutes.
5. Choose an AI voice: Coral, Alloy, or Onyx.
6. Click **Generate podcast**.
7. Follow the generation progress.
8. Read the generated transcript and listen to the audio.
9. Download the MP3 if needed.

You can start with `examples/lesson_notes.txt` or one of the demonstration files included in this repository.

## Demo and Example Outputs

The `demo/` directory contains a sample input and its generated podcast output, allowing the project to be evaluated without making additional OpenAI API calls.

| File | Description |
|---|---|
| [sample_source.txt](demo/sample_source.txt) | Example educational source text. |
| [sample_script.txt](demo/sample_script.txt) | Generated podcast script. |
| [sample_lesson_recap.mp3](demo/sample_lesson_recap.mp3) | Generated AI-narrated MP3 podcast. |

Additional sample input is available in [examples/lesson_notes.txt](examples/lesson_notes.txt).

Newly generated MP3 files are stored in `outputs/`. These runtime outputs are normally excluded from Git, while selected demo files are included for evaluation.

## Testing and Validation

The project uses pytest and automated tests with mocked API interactions.

**Latest team-verified result: 14 automated tests passed.**

Run the test suite with:

```bash
python -m pytest -q
```

Automated tests verify application logic without making paid OpenAI API requests.

The team also performed manual end-to-end validation, including:

- Running the application on Windows and macOS.
- Generating a Lesson Recap using real OpenAI API calls.
- Generating an Exam Preparation podcast.
- Verifying AI narration and MP3 output.
- Playing and downloading generated audio.
- Checking progress messages and input-validation behavior.
- Reviewing Git changes and integrating contributions using Pull Requests.

Automated tests do not replace a real end-to-end test, particularly for audio quality and external API availability.

## Development Workflow and Collaboration

Podcast Studio was developed collaboratively by two contributors using GitHub.

The team worked with:

- Separate feature branches.
- Pull Requests and peer review.
- Automated tests before merging changes.
- Independent development environments on Windows and macOS.
- Integration testing of the completed application.

The implementation includes independent modules for input processing, LLM interaction, speech generation, and the user interface.

GitHub commit and Pull Request history documents the team's contributions.

## Challenges and Solutions

**1. OpenAI model access**

An attempted TTS model returned an access error. The team resolved the issue by configuring a supported model (`tts-1`).

**2. Cross-platform environments**

Windows and macOS used different Python environments. The team standardized the required Python version, dependencies, and environment configuration.

**3. Integrating separately developed modules**

The modular structure, automated tests, feature branches, and Pull Request reviews helped integrate different parts of the project safely.

**4. User experience during generation**

Generating a podcast involves multiple processing stages and can take time. Progress reporting and clearer error messages were added to make the application easier to use.

## Known Limitations

- **PDF extraction:** Only PDFs containing selectable text are supported. Scanned PDFs require OCR, which is not implemented.
- **Approximate duration:** A 3- or 5-minute target does not guarantee exact audio length.
- **API dependency:** Real script and speech generation require OpenAI access, a valid API key, and available billing.
- **Processing time:** Long source documents and audio outputs may require additional API requests and more processing time.
- **LLM accuracy:** AI-generated scripts and exam questions may contain inaccuracies and should be reviewed for important educational use cases.
- **Temporary files:** Locally generated outputs are not automatically permanent or synchronized across computers.
- **Public deployment:** Production use would require stronger security, user authentication, usage limits, privacy protections, and appropriate data-retention controls.

## Optional Cloud Deployment

Podcast Studio can be configured for deployment on a Python-compatible hosting service such as Render.

A possible Render configuration is:

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `python app.py`
- **Environment variables:** `OPENAI_API_KEY`, `OPENAI_LLM_MODEL`, `OPENAI_TTS_MODEL`
- **Recommended access protection:** `GRADIO_AUTH_USER` and `GRADIO_AUTH_PASSWORD`

The application's entry point supports the server host and port configuration needed for cloud environments.

Audio concatenation also requires FFmpeg to be available in the deployment environment.

**Cloud deployment is optional and should be tested separately.** This README does not claim that a permanent public instance is currently running.

For temporary sharing, Gradio can generate a public share URL when configured accordingly. Such URLs are temporary and should not be treated as permanent hosting.

OpenAI API usage incurs separate costs. Public deployment should use appropriate access controls and spending limits.

## Future Improvements

Potential next steps include:

- More podcast formats and narration styles.
- More configurable exam preparation options.
- Support for scanned PDFs using OCR.
- Permanent cloud hosting with authentication and request quotas.
- Better cost tracking and usage controls.
- Additional usability and accessibility improvements.

## Project Assets

- `examples/lesson_notes.txt` — example lesson input.
- `demo/` — demonstration source text, script, and MP3.
- `outputs/` — locally generated MP3 files.
- `.env.example` — safe environment configuration template.
- `requirements.txt` — application dependencies.
- `requirements-dev.txt` — development and testing dependencies.
- `tests/` — automated test suite.

---

**Podcast Studio** demonstrates how a modular Python application can combine text processing, generative AI, text-to-speech, and a simple web interface into a practical educational tool.