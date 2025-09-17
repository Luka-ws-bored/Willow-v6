"""
Vector DB helpers for Willow (scaffold).
These functions are placeholders and raise NotImplementedError until we implement FAISS/embeddings.
"""
from typing import List, Dict, Any


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Return embeddings for list of texts.

    Placeholder: integrate sentence-transformers or Ollama embedding API later.
    """
    raise NotImplementedError("embed_texts not implemented yet")


def create_index(embeddings: List[List[float]], ids: List[str], index_path: str) -> None:
    """Create and persist a vector index (FAISS)."""
    raise NotImplementedError("create_index not implemented yet")


def load_index(index_path: str) -> Any:
    """Load and return an index object."""
    raise NotImplementedError("load_index not implemented yet")


def search_index(query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """Search index and return top_k results as list of dicts {id:..., score:..., metadata:...}.

    Placeholder until FAISS integration.
    """
    raise NotImplementedError("search_index not implemented yet")