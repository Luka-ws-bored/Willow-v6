@echo off
REM run_demo.bat - Windows demo script for Willow v6 RAG integration

echo 🚀 Willow v6 RAG Integration Demo
echo ==================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.9+.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "demo_rag_integration.py" (
    echo ❌ demo_rag_integration.py not found. Please run from Willow v6 root directory.
    pause
    exit /b 1
)

REM Run the demo
echo Running RAG integration demo...
python demo_rag_integration.py

echo.
echo ✅ Demo completed!
echo.
echo 📚 Next steps:
echo    • Install RAG dependencies: pip install -r requirements-rag.txt
echo    • Try the examples in README.md
echo    • Run tests: python -m pytest tests/
echo.
pause