from willow.llm_router import get_response

if __name__ == "__main__":
    prompt = "Explain the theory of relativity in simple terms."
    response = get_response(prompt)
    print("Local LLM Response:", response)
