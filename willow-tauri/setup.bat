@echo off
REM Willow Desktop Setup Script for Windows
echo.
echo 🌲 Willow Desktop v6.0.0 Setup
echo ================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js is not installed. Please install Node.js first:
    echo    https://nodejs.org/
    pause
    exit /b 1
)

REM Check if npm is available
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ npm is not available. Please install Node.js with npm.
    pause
    exit /b 1
)

echo ✅ Node.js found
node --version

REM Install frontend dependencies
echo.
echo 📦 Installing frontend dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)

echo ✅ Frontend dependencies installed

REM Check if Rust is installed
where cargo >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️  Rust is not installed. To complete the setup:
    echo.
    echo 1. Install Rust from: https://rustup.rs/
    echo 2. Restart your terminal
    echo 3. Run this script again or manually install Tauri CLI:
    echo    cargo install tauri-cli
    echo.
    echo Frontend is ready, but you'll need Rust for building the desktop app.
    pause
    exit /b 0
)

echo ✅ Rust found
cargo --version

REM Install Tauri CLI
echo.
echo 🔧 Installing Tauri CLI...
cargo install tauri-cli --version "^1.4"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install Tauri CLI
    pause
    exit /b 1
)

echo ✅ Tauri CLI installed

echo.
echo 🎉 Setup complete! You can now:
echo.
echo   • Run in development mode: npm run tauri:dev
echo   • Build for production: npm run tauri:build
echo   • Test frontend only: npm run dev
echo.
echo 📚 Make sure the Willow v6 Python backend is available in the parent directory.
echo.
pause