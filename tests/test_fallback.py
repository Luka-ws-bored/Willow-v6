import sys
import os
import importlib.util

# Add src directory to Python path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'willow-dev', 'src')

# Import the main module dynamically to avoid linter issues
main_path = os.path.join(src_path, "main.py")
spec = importlib.util.spec_from_file_location("main", main_path)
if spec is not None and spec.loader is not None:
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)
    query_llm = main_module.query_llm
else:
    raise ImportError("Could not load main module")

# This test calls query_llm with explicit models where the first model is assumed to be slow.
# It verifies that the function falls back to the next available model and returns non-error output.

def test_fallback_to_smaller_model():
    # Provide a simple prompt. If primary times out or fails, the smaller model should answer.
    prompt = 'Say OK in one word.'
    # Explicit model list: primary (expected to be slow) then a lightweight fallback
    models = ['goekdenizguelmez/josiefied-qwen3:1.7b', 'qwen3:0.6b']
    resp = query_llm(prompt, models=models)
    assert resp and 'Error' not in resp, f'Fallback failed, response: {resp}'

if __name__ == '__main__':
    print('Running fallback test...')
    test_fallback_to_smaller_model()
    print('Fallback test finished.')