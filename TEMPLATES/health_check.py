"""
Health Check Template for Willow Components
"""
import sys
import importlib.util


def check_import(module_name):
    """Check if a module can be imported."""
    try:
        importlib.util.find_spec(module_name)
        print(f"✓ {module_name} - OK")
        return True
    except ImportError:
        print(f"✗ {module_name} - MISSING")
        return False


def main():
    """Run health checks."""
    print("Willow Health Check")
    print("=" * 20)
    
    # Check core dependencies
    modules_to_check = [
        "requests",
        "os",
        "sys",
        "typing"
    ]
    
    all_good = True
    for module in modules_to_check:
        if not check_import(module):
            all_good = False
    
    print("\n" + "=" * 20)
    if all_good:
        print("All core dependencies are available!")
        return 0
    else:
        print("Some dependencies are missing!")
        return 1


if __name__ == "__main__":
    sys.exit(main())