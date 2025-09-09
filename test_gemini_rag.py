from rag.llm_router import get_llm
from rag.rag_chain import build_qa_chain
from langchain.vectorstores.faiss import FAISS
from langchain.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from rag.config import gemini_api_key, retrieval_k

# Load documents
loader = TextLoader("sample_docs.txt")  # Replace with your test file
docs = loader.load()

# Embed and store
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=gemini_api_key)
db = FAISS.from_documents(docs, embedding_model)

# Build chain
llm = get_llm()
rag_chain = build_qa_chain(llm, db.as_retriever(search_kwargs={"k": retrieval_k}))

# Ask a question
query = "What is Willow?"
response = rag_chain.run(query)
print("Answer:", response)
