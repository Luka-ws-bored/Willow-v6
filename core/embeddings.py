# core/embeddings.py
from abc import ABC, abstractmethod
import os
import logging
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)

class EmbeddingStore(ABC):
    @abstractmethod
    def upsert(self, id: str, vector: List[float], metadata: Dict = None):
        raise NotImplementedError

    @abstractmethod
    def query(self, vector: List[float], k: int = 5) -> List[Tuple[str, float, Dict]]:
        raise NotImplementedError

class ChromaStore(EmbeddingStore):
    def __init__(self, url: str = None, persist_directory: str = "infra/chroma-data"):
        self.url = url or os.environ.get("CHROMA_URL", "http://localhost:8000")
        self.persist_directory = persist_directory
        # Lazy import so tests don't require chroma installed
        try:
            import chromadb
            from chromadb.config import Settings
            self._client = chromadb.Client(Settings(chroma_api_impl="rest", chroma_server_host=self.url.replace("http://","").split(":")[0], chroma_server_http_port=int(self.url.split(":")[-1]) if ":" in self.url else 8000))
            self._col = None
        except Exception as e:
            logger.debug("Chroma client not initialized: %s", e)
            self._client = None
            self._col = None

    def _ensure_col(self, name="willow"):
        if not self._client:
            raise RuntimeError("Chroma client not configured")
        if self._col is None:
            try:
                self._col = self._client.get_collection(name)
            except Exception:
                self._col = self._client.create_collection(name=name)
        return self._col

    def upsert(self, id: str, vector: List[float], metadata: Dict = None):
        col = self._ensure_col()
        col.upsert(ids=[id], documents=[metadata.get("text") if metadata else ""], embeddings=[vector], metadatas=[metadata or {}])

    def query(self, vector: List[float], k: int = 5) -> List[Tuple[str, float, Dict]]:
        col = self._ensure_col()
        res = col.query(query_embeddings=[vector], n_results=k, include=["metadatas","distances","ids"])
        ids = res["ids"][0]
        distances = res["distances"][0]
        metadatas = res["metadatas"][0]
        return list(zip(ids, distances, metadatas))