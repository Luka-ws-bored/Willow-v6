import os
import sys
import importlib.util
import time

# Import setup
project_root = os.path.abspath('.')
src_path = os.path.join(project_root, 'willow-dev', 'src')
main_path = os.path.join(src_path, 'main.py')
spec = importlib.util.spec_from_file_location('main', main_path)
if spec is not None and spec.loader is not None:
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)
    query_llm = main_module.query_llm
else:
    raise ImportError(f"Could not load main module from {main_path}")

print('Quick sanity test with smaller model...')
start = time.time()
resp = query_llm('Hello, introduce yourself in one sentence.', 'qwen3:0.6b')
elapsed = time.time() - start
print(f'Response ({elapsed:.2f}s): {resp}')