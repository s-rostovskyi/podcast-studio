"""Gradio interface for lesson recap and exam preparation podcasts."""

import logging
import os
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    PermissionDeniedError,
    RateLimitError,
)

from src.data_processor import prepare_input
from src.llm_processor import create_script
from src.tts_generator import generate_audio


# Load local environment configuration.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

logger = logging.getLogger(__name__)


def make_recap(
    file_path,
    notes,
    duration,
    voice,
    mode="recap",
    progress=gr.Progress(),
):
    """Convert lesson notes into a podcast script and MP3 audio."""

    try:
        # Step 1: Validate and prepare the input.
        progress(0.05, desc="Processing lesson notes...")

        text = prepare_input(notes, file_path)

        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OpenAI API key is not configured. "
                "Please check your environment settings."
            )

        # Step 2: Generate the podcast script.
        progress(0.30, desc="Generating podcast script...")

        script = create_script(
            text,
            duration_minutes=int(duration),
            mode=mode,
        )

        # Step 3: Convert the script into audio.
        progress(0.65, desc="Creating MP3 audio...")

        mp3_path = generate_audio(script, voice=voice)

        # Step 4: Finish the processing pipeline.
        progress(1.0, desc="Podcast ready!")

        return script, mp3_path, mp3_path

    # Input validation and configuration errors.
    except ValueError as exc:
        raise gr.Error(str(exc)) from exc

    # Invalid or expired OpenAI API key.
    except AuthenticationError as exc:
        logger.warning("OpenAI authentication failed.")
        raise gr.Error(
            "OpenAI authentication failed. Check your API key."
        ) from exc

    # Model access or project permissions.
    except PermissionDeniedError as exc:
        logger.warning("OpenAI access denied (403).")
        raise gr.Error(
            "OpenAI access denied. Check model availability "
            "and your API project permissions."
        ) from exc

    # Rate limits or API quota problems.
    except RateLimitError as exc:
        logger.warning("OpenAI rate limit or quota reached.")
        raise gr.Error(
            "OpenAI rate limit or quota reached. "
            "Please try again later or check your API billing."
        ) from exc

    # Invalid request parameters or unavailable model settings.
    except BadRequestError as exc:
        logger.warning("OpenAI rejected the request.")
        raise gr.Error(
            "OpenAI rejected the request. "
            "Check the model configuration and input."
        ) from exc

    # Network connectivity and request timeouts.
    except APIConnectionError as exc:
        logger.warning("OpenAI connection failed.")
        raise gr.Error(
            "Could not connect to OpenAI. "
            "Please check your internet connection and retry."
        ) from exc

    # Other API status errors.
    except APIStatusError as exc:
        logger.warning("OpenAI API returned status %s.", exc.status_code)
        raise gr.Error(
            f"OpenAI returned an error (HTTP {exc.status_code}). "
            "Please try again later."
        ) from exc

    # Preserve Gradio errors without wrapping them again.
    except gr.Error:
        raise

    # Unexpected internal errors.
    except Exception as exc:
        logger.exception("Unexpected podcast generation failure.")
        raise gr.Error(
            "An unexpected error occurred while generating the podcast. "
            "Please check the application logs."
        ) from exc


# Build the web interface.
with gr.Blocks(title="Podcast Studio - Lesson Recapper") as demo:

    gr.Markdown(
        "# Podcast Studio\n"
        "### Turn your lesson notes into an AI-powered audio podcast"
    )

    gr.Markdown(
        "Upload a **PDF, TXT or MD** document, paste your notes, "
        "or use both. Choose your learning mode and generate a "
        "podcast with AI narration."
    )

    # Input section.
    with gr.Row():
        source_file = gr.File(
            label="Upload lesson notes (PDF, TXT, MD)",
            file_types=[".pdf", ".txt", ".md"],
            type="filepath",
        )

        notes = gr.Textbox(
            label="Or paste your notes",
            lines=9,
            placeholder="Paste your lesson notes or transcript here...",
        )

    # Podcast settings.
    with gr.Row():
        duration = gr.Dropdown(
            choices=[3, 5],
            value=5,
            label="Target duration (minutes)",
            info="Approximate duration; actual audio length may vary.",
        )

        voice = gr.Dropdown(
            choices=["coral", "alloy", "onyx"],
            value="coral",
            label="AI voice",
            info="Select the voice used for narration.",
        )

    # Learning mode selection.
    mode = gr.Radio(
        choices=[
            ("Lesson Recap", "recap"),
            ("Exam Preparation", "exam"),
        ],
        value="recap",
        label="Learning mode",
        info="Choose a short recap or a podcast with review questions.",
    )

    gr.Markdown(
        "**Lesson Recap:** A concise explanation of the main ideas.\n\n"
        "**Exam Preparation:** Key concepts followed by three "
        "self-check questions and answers."
    )

    # Generate button.
    generate_button = gr.Button(
        "Generate podcast",
        variant="primary",
    )

    # Generated output.
    script = gr.Textbox(
        label="Podcast script (transcript)",
        lines=12,
        interactive=False,
    )

    audio = gr.Audio(
        label="Listen to your podcast",
        interactive=False,
    )

    download = gr.File(
        label="Download podcast MP3",
    )

    gr.Markdown(
        "*Audio narration is AI-generated. "
        "Long documents may require multiple API requests. "
        "OpenAI API usage may incur costs.*"
    )

    # Connect the interface to the processing pipeline.
    generate_button.click(
        fn=make_recap,
        inputs=[source_file, notes, duration, voice, mode],
        outputs=[script, audio, download],
        concurrency_limit=1,
    )

# Enable queued execution and progress reporting.
demo.queue()
