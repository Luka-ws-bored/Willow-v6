from willow.llm.local_llm import run_local_llm

def test_ollama():
    print("Testing Ollama LLM connection...")
    prompt = "Hello! Please respond with a short greeting."
    print(f"\nPrompt: {prompt}")
    response = run_local_llm(prompt)
    print(f"\nResponse: {response}")

if __name__ == "__main__":
    test_ollama()
