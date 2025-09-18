@echo off
echo Starting Willow development environment...
echo.

echo Starting frontend development server...
start cmd /k "cd %~dp0..\willow-tauri\frontend && npm run dev"

echo Starting backend server...
start cmd /k "cd %~dp0.. && .\.venv\Scripts\activate && python -m flask run --port 5000"

echo.
echo Frontend will be available at http://localhost:1420
echo Backend will be available at http://localhost:5000
echo.
echo Press any key to exit...
pause >nul