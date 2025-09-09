import os
from streamlit import title, text_input, button, write
from dotenv import load_dotenv
from willow.llm_router import get_response

load_dotenv()
title("Willow v6 Chat (with RAG)")

user_input = text_input("Ask a question:")
if button("Send"):
    answer = get_response(user_input)
    write("**Answer:**", answer)
