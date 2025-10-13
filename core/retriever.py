# core/retriever.py
from typing import List, Dict, Tuple
from core.embeddings import EmbeddingStore
import logging

logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self, embedding_store: EmbeddingStore, bm25=None):
        self.embedding_store = embedding_store
        self.bm25 = bm25  # optional BM25 instance for hybrid re-rank

    def retrieve(self, query_text: str, query_vector: List[float], top_k: int = 5) -> List[Dict]:
        # 1) vector query
        hits = []
        try:
            hits = self.embedding_store.query(query_vector, k=top_k)
        except Exception as e:
            logger.exception("Vector DB query failed: %s", e)
            hits = []

        results = []
        for id_, score, metadata in hits:
            results.append({"id": id_, "score": score, "metadata": metadata})

        # Optionally re-rank with BM25 if available (sketch)
        if self.bm25:
            # bm25 should provide scores over ids or docs
            # implement hybrid ranking as needed
            pass

        return results