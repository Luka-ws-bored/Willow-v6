import logging
import threading
import time
from typing import Dict

logger = logging.getLogger(__name__)

class Subconscious:
    def __init__(self, memory_manager, dream_interval: int = 3600):
        self.memory = memory_manager
        self.interval = dream_interval
        self.thread = threading.Thread(target=self._dream_loop, daemon=True)

    def start(self):
        logger.info("Subconscious agent started")
        self.thread.start()

    def _dream_loop(self):
        while True:
            time.sleep(self.interval)
            self._dream()

    def _dream(self):
        # Example: summarize recent memory
        recent = self.memory.get_recent(10)
        summary = "; ".join([str(entry) for entry in recent])
        logger.info(f"Subconscious dream summary: {summary}")
        self.memory.add_entry({"event": "dream", "summary": summary})

    # New method: manual dream trigger
    def dream(self) -> str:
        recent = self.memory.get_recent(10)
        summary = "; ".join([str(entry) for entry in recent])
        self.memory.add_entry({"event": "dream_manual", "summary": summary})
        return f"Dream summary: {summary}"

    # New: evaluate multiple provider responses
    def evaluate_responses(self, responses: Dict[str, str]) -> str:
        """
        Choose the best response among multiple providers.
        Current heuristic: longest non-error response.
        """
        best_provider, best_resp = None, ""
        for prov, resp in responses.items():
            if resp.startswith("[FALLBACK ERROR]"):
                continue
            if len(resp) > len(best_resp):
                best_resp = resp
                best_provider = prov
        chosen = best_resp or "[FALLBACK ERROR] All providers failed."
        logger.info(f"Subconscious picked provider: {best_provider}")
        return chosen 