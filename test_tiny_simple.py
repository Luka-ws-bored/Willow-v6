import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tiny_helper import select_model

if __name__ == "__main__":
    print("🔍 Testing Tiny Helper model selection...")
    model = select_model()
    print(f"✅ Selected model: {model}")
    print("🎉 Tiny Helper integration successful!")