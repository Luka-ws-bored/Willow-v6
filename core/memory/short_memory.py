# core/memory/short_memory.py
from typing import List, Dict

class ShortMemory:
    def __init__(self, max_messages: int = 32):
        self.max_messages = max_messages
        self.buffer: List[Dict] = []

    def append(self, message: Dict):
        self.buffer.append(message)
        if len(self.buffer) > self.max_messages:
            self.buffer.pop(0)

    def get(self) -> List[Dict]:
        return list(self.buffer)

    def clear(self):
        self.buffer = []