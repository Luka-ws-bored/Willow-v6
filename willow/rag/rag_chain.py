from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from .llm_wrapper import load_gemini_llm, load_gemini_embeddings

# Load docs
def load_docs(path="docs/sample.txt"):
    loader = TextLoader(path)
    docs = loader.load()
    return docs

# Chunk docs
def chunk_docs(docs, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(docs)

# Build RAG QA chain
def build_qa_chain(doc_path="docs/sample.txt"):
    docs = load_docs(doc_path)
    chunks = chunk_docs(docs)
    embeddings = load_gemini_embeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    retriever = vector_store.as_retriever()
    llm = load_gemini_llm()
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
    return qa

def res(query, doc_path="docs/sample.txt"):
    qa = build_qa_chain(doc_path)
    result = qa({"query": query})
    return result
