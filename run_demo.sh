#!/bin/bash
# run_demo.sh - Cross-platform demo script for Willow v6 RAG integration

echo "🚀 Willow v6 RAG Integration Demo"
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.9+."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

echo "Using Python: $PYTHON_CMD"

# Check if we're in the right directory
if [ ! -f "demo_rag_integration.py" ]; then
    echo "❌ demo_rag_integration.py not found. Please run from Willow v6 root directory."
    exit 1
fi

# Run the demo
echo "Running RAG integration demo..."
$PYTHON_CMD demo_rag_integration.py

echo ""
echo "✅ Demo completed!"
echo ""
echo "📚 Next steps:"
echo "   • Install RAG dependencies: pip install -r requirements-rag.txt"
echo "   • Try the examples in README.md"
echo "   • Run tests: python -m pytest tests/"