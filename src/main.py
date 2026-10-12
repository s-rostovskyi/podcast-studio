"""Gradio interface connecting input processing, LLM generation and TTS."""
import logging
import os
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from src.data_processor import prepare_input
from src.llm_processor import create_script
from src.tts_generator import generate_audio

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
logger = logging.getLogger(__name__)

def make_recap(file_path, notes, duration, voice):
    """Full input -> script -> MP3 pipeline invoked by the Gradio button."""
    try:
        text = prepare_input(notes, file_path)
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is not configured on the server.")
        script = create_script(text, duration_minutes=int(duration))
        mp3_path = generate_audio(script, voice=voice)
        return script, mp3_path, mp3_path
    except ValueError as exc:
        raise gr.Error(str(exc)) from exc
    except Exception as exc:
        logger.exception("Podcast generation failed")
        raise gr.Error("Podcast generation failed. Check API balance, model access and server logs.") from exc

with gr.Blocks(title="Podcast Studio - Lesson Recapper") as demo:
    gr.Markdown("# Podcast Studio\n### Turn lesson notes into an AI-narrated recap")
    gr.Markdown("Upload a PDF/TXT/MD file, paste text, or use both. The podcast voice is AI-generated, not human.")
    with gr.Row():
        source_file = gr.File(label="Upload lesson notes", file_types=[".pdf", ".txt", ".md"], type="filepath")
        notes = gr.Textbox(label="Or paste your notes", lines=9, placeholder="Paste your lesson transcript or notes here...")
    with gr.Row():
        duration = gr.Dropdown([3, 5], value=5, label="Target duration (minutes)")
        voice = gr.Dropdown(["coral", "alloy", "onyx"], value="coral", label="AI voice")
    generate_button = gr.Button("Generate podcast", variant="primary")
    script = gr.Textbox(label="Podcast script (transcript)", lines=12)
    audio = gr.Audio(label="Listen to the MP3", interactive=False)
    download = gr.File(label="Download podcast MP3")
    gr.Markdown("*Large transcripts can require several API calls. This demo uses your configured OpenAI API billing account.*")
    generate_button.click(
        fn=make_recap,
        inputs=[source_file, notes, duration, voice],
        outputs=[script, audio, download],
        concurrency_limit=1,
    )
