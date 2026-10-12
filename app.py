"""App entrypoint for local development and cloud deployment."""
import os
from dotenv import load_dotenv
from src.main import demo

load_dotenv()

if __name__ == "__main__":
    # Local: 127.0.0.1. Cloud providers: bind publicly to 0.0.0.0 and $PORT.
    host = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0" if os.getenv("PORT") or os.getenv("SPACE_ID") else "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("GRADIO_SERVER_PORT", "7860")))
    username, password = os.getenv("GRADIO_AUTH_USER"), os.getenv("GRADIO_AUTH_PASSWORD")
    auth = (username, password) if username and password else None
    demo.launch(server_name=host, server_port=port, share=os.getenv("GRADIO_SHARE") == "1", auth=auth)
