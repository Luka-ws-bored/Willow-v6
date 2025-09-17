import sys
import os
import importlib.util

# Import setup with proper null checks
src_path = os.path.join('.', 'willow-dev', 'src')
main_path = os.path.join(src_path, 'main.py')

# Check if file exists before attempting import
if not os.path.exists(main_path):
    raise FileNotFoundError(f"Module file not found: {main_path}")

spec = importlib.util.spec_from_file_location('main', main_path)
if spec is None:
    raise ImportError(f"Could not create module spec for {main_path}")

if spec.loader is None:
    raise ImportError(f"Module spec has no loader for {main_path}")

main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)
query_llm = main_module.query_llm

print('Testing fallback with smaller model only...')
# Test directly with fallback models to verify they work
resp = query_llm('Say OK', ['qwen3:0.6b'])
print('Fallback response:', resp)