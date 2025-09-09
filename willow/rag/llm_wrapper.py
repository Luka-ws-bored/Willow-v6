from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def load_gemini_llm(model="gemini-2.5-pro"):
    llm = ChatGoogleGenerativeAI(model=model)
    return llm

def load_gemini_embeddings(model="text-embedding-gecko"):
    embed = GoogleGenerativeAIEmbeddings(model=model)
    return embed
