import os
import json
import time

# Import the LLM query function from the project
# Using dynamic import approach to avoid linter issues (learned from previous import problems)
import sys
import importlib.util

# Add src directory to Python path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'willow-dev', 'src')

def import_query_llm():
    """Dynamically import query_llm function with proper error handling"""
    # Use dynamic import to avoid linter issues
    main_path = os.path.join(src_path, "main.py")
    if os.path.exists(main_path):
        spec = importlib.util.spec_from_file_location("main", main_path)
        if spec is not None and spec.loader is not None:
            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)
            return main_module.query_llm
    raise ImportError("Could not import query_llm function")

# Import the function
query_llm = import_query_llm()

# Load constitution to test constitution-influence
CONFIG_PATH = os.path.join(project_root, 'willow-dev', 'config', 'core_constitution.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    constitution = json.load(f)


def pretty_print(title, elapsed, resp):
    print('\n' + '='*8 + f' {title} (%.2fs) ' % elapsed + '='*8)
    print(resp)


def test_raw_response():
    prompt = "Hello Willow, introduce yourself in two friendly, concise sentences."
    start = time.time()
    resp = query_llm(prompt)
    elapsed = time.time() - start
    pretty_print('RAW RESPONSE', elapsed, resp)


def test_constitution_influence():
    # Use the Identity description to guide the model. Keep this short to avoid long prompt.
    identity_desc = constitution.get('Identity', {}).get('description', '')
    prompt = (
        f"Follow this assistant identity before answering: {identity_desc}\n\n"
        "Now: Introduce yourself in two friendly, concise sentences."
    )
    start = time.time()
    resp = query_llm(prompt)
    elapsed = time.time() - start
    pretty_print('CONSTITUTION INFLUENCED RESPONSE', elapsed, resp)


if __name__ == '__main__':
    print('Running Willow sanity tests...')
    test_raw_response()
    test_constitution_influence()
    print('\nSanity test complete.')