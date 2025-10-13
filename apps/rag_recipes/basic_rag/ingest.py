# apps/rag_recipes/basic_rag/ingest.py
from core.embeddings import ChromaStore
from core.llm_adapter import OllamaAdapter

def main():
    store = ChromaStore()
    # Example ingest: small docs
    docs = [
        {"id":"doc_1","text":"Lagos is the largest city in Nigeria..."},
        {"id":"doc_2","text":"Getting around Lagos: local tips..."}
    ]
    adapter = OllamaAdapter()
    # For prototype: call adapter.embed if implemented; else skip
    print("Ingest placeholder — implement embedding and upsert with ChromaStore.")

if __name__ == "__main__":
    main()