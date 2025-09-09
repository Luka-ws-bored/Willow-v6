import os
from rag.config import LLM_MODE
from rag.llm_router import get_llm
from rag.rag_chain import build_qa_chain

def main():
    print(f"Using LLM mode: {LLM_MODE}")
    llm = get_llm()
    # Load documents, build retriever, and run test query
    # Same as test_gemini_rag.py logic here

if __name__ == "__main__":
    main()
