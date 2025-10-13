# apps/rag_recipes/basic_rag/query.py
from core.retriever import Retriever
from core.embeddings import ChromaStore
from core.llm_adapter import OllamaAdapter

def main():
    store = ChromaStore()
    retriever = Retriever(store)
    adapter = OllamaAdapter()
    q = "What are transport tips in Lagos?"
    # TODO: get embedding via adapter or other embedder
    print("Query placeholder — implement embed->retrieve->llm chain")

if __name__ == "__main__":
    main()