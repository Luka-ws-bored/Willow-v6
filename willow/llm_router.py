import os
from willow.llm.local_llm import run_local_llm

def get_response(prompt: str) -> str:
    # Always use local for now; override in the future if needed
    return run_local_llm(prompt)

if __name__ == "__main__":
    test_prompt = "What is the capital of France?"
    print("Response:", get_response(test_prompt))
