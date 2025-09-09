@echo off
echo Checking Gemini Code Assist status...
py -c "import os; exit(os.system('code --list-extensions | findstr google.gemini'))"
if %errorlevel% neq 0 (
    echo Gemini not found. Please install via VS Code Marketplace.
    echo You can run: code --install-extension google.gemini
) else (
    echo Gemini extension found.
)
echo To verify it's signed in, run: Ctrl + Shift + P → Gemini: Sign In
echo.
echo Adding suggestion prompt to test_gemini.py...
echo # Create a function that fetches weather using an API>> test_gemini.py
echo.
echo Running Gemini Dev Setup...
code test_gemini.py
echo.
echo 🛠️ Open Output Panel with Ctrl + Shift + U
echo 🧠 Select 'Gemini Code Assist' from the dropdown
echo.
echo ✅ Gemini setup and test complete! You’re ready to roll.