
import asyncio

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, Input, RichLog, Static

from backend.orchestrator import HardwareAssistant


class HardwareChatApp(App):

    TITLE = "Linux Hardware Q&A Assistant"
    SUB_TITLE = "Local AI • Ollama • Qwen2.5"

    CSS = """
    Screen {
        background: $surface;
    }

    #welcome {
        height: auto;
        padding: 1 2;
        color: $text;
    }

    #chat {
        height: 1fr;
        border: round $primary;
        padding: 1;
        margin: 0 1;
    }

    #question {
        margin: 1;
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.assistant = HardwareAssistant()

    def compose(self) -> ComposeResult:
        yield Header()

        yield Static(
            "Ask questions about your Linux CPU, memory, storage, GPU "
            "and operating system.\n"
            "Type 'exit' or 'quit' to close the assistant.",
            id="welcome",
        )

        yield RichLog(
            id="chat",
            wrap=True,
            markup=False,
        )

        yield Input(
            placeholder="Ask a hardware question and press Enter...",
            id="question",
        )

        yield Footer()

    def on_mount(self):
        chat = self.query_one("#chat", RichLog)

        chat.write("Hardware Assistant is ready.")
        chat.write("Your questions are processed using the local Ollama model.")
        chat.write("-" * 60)

        self.query_one("#question", Input).focus()

    async def on_input_submitted(self, event: Input.Submitted):

        question = event.value.strip()

        if not question:
            return

        event.input.value = ""

        if question.lower() in {"exit", "quit"}:
            self.exit()
            return

        chat = self.query_one("#chat", RichLog)

        chat.write(f"\nYou: {question}")
        chat.write("Assistant: Thinking...")

        event.input.disabled = True

        try:
            answer = await asyncio.to_thread(
                self.assistant.ask,
                question,
            )

            chat.write(f"Assistant: {answer}")

        except Exception:
            chat.write(
                "Assistant: Something went wrong while processing your question."
            )

        finally:
            event.input.disabled = False
            event.input.focus()
