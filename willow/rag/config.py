import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY", "sk-...")
gemini_api_key = os.getenv("GEMINI_API_KEY", "")
retrieval_k = 5
chunk_size = 300
