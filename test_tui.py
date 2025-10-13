import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Set environment variable to point to a mock API
os.environ['API_BASE'] = 'http://localhost:8080/api/v1'

def test_tui_import():
    try:
        from apps.tui_demo.tui_app import WillowTUI
        print("✓ TUI application imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import TUI application: {e}")
        return False

if __name__ == "__main__":
    success = test_tui_import()
    if success:
        print("TUI application is ready to run once backend is available")
    else:
        print("Please check the import errors above")