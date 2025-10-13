# core/memory/long_memory.py
from typing import Optional, Dict, List
from core.embeddings import EmbeddingStore

class LongMemory:
    def __init__(self, embedding_store: EmbeddingStore):
        self.embedding_store = embedding_store

    def persist(self, id: str, text: str, metadata: Optional[Dict] = None):
        # use an embedder to generate vector (we expect embedder integrated via core.llm_adapter or separate)
        # For now, expect caller supplies vector in metadata or implement later
        raise NotImplementedError("Implement persist using embedding model/adapter")

    def query(self, text: str, k: int = 5):
        # similar: embed the text, query embedding_store
        raise NotImplementedError("Implement query using embedding model/adapter")