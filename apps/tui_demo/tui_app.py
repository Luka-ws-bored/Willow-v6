# apps/tui_demo/tui_app.py
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, Input, Static, Button
import asyncio
import httpx
import os

API_BASE = os.environ.get("API_BASE", "http://localhost:8080/api/v1")

class WillowTUI(App):
    CSS_PATH = None
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Welcome to Willow TUI — type a prompt and press Enter", id="intro")
        yield Input(placeholder="Type prompt here...", id="prompt_input")
        yield Button("Send", id="send_btn")
        yield Static("", id="out")
        yield Footer()

    async def on_button_pressed(self, event):
        if event.button.id == "send_btn":
            inp = self.query_one("#prompt_input")
            prompt = inp.value
            await self.call_llm(prompt)

    async def on_input_submitted(self, event):
        prompt = event.value
        await self.call_llm(prompt)

    async def call_llm(self, prompt: str):
        out_widget = self.query_one("#out", Static)
        out_widget.update("Thinking...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                r = await client.post(f"{API_BASE}/chat", json={"model":"llama2","messages":[{"role":"user","content":prompt}]})
                r.raise_for_status()
                data = r.json()
                out_widget.update(str(data))
            except Exception as e:
                out_widget.update(f"Error: {e}")

if __name__ == "__main__":
    WillowTUI().run()