import logging
import threading
import time

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