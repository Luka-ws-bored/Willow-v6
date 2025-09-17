@echo off
REM Post-Rust Installation Setup for Willow v6
echo.
echo 🦀 Willow v6 Post-Rust Installation Setup
echo ========================================
echo.

REM Update PATH for this session
set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"

echo [1/6] Verifying Rust installation...
rustup --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Rust not accessible. Please restart terminal.
    pause
    exit /b 1
)

cargo --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Cargo not accessible.
    pause
    exit /b 1
)

echo ✅ Rust and Cargo working!
echo.

echo [2/6] Installing rustfmt component...
rustup component add rustfmt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install rustfmt
    pause
    exit /b 1
)

rustfmt --version
echo ✅ rustfmt installed and working!
echo.

echo [3/6] Installing Tauri CLI globally...
npm install -g @tauri-apps/cli
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install Tauri CLI
    pause
    exit /b 1
)
echo ✅ Tauri CLI installed!
echo.

echo [4/6] Navigating to frontend directory...
cd /d "c:\Users\User\Downloads\Willow v6\willow-tauri\frontend"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Frontend directory not found
    pause
    exit /b 1
)
echo ✅ In frontend directory: %CD%
echo.

echo [5/6] Installing frontend dependencies...
npm install
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)
echo ✅ Frontend dependencies installed!
echo.

echo [6/6] Testing Tauri setup...
npm run tauri --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Tauri CLI accessible from project
    npm run tauri --version
) else (
    echo ⚠️ Tauri CLI may need global installation verification
)

echo.
echo 🎉 Willow v6 Development Environment Setup Complete!
echo.
echo ✅ Rust: Installed and verified
echo ✅ Cargo: Working
echo ✅ rustfmt: Installed
echo ✅ Tauri CLI: Installed globally
echo ✅ Frontend deps: Installed
echo.
echo 🚀 Ready to start development:
echo    npm run tauri:dev
echo.
echo 📝 VSCode Extensions to install:
echo    - rust-lang.rust-analyzer
echo    - tauri-apps.tauri-vscode
echo    - esbenp.prettier-vscode
echo    - dsznajder.es7-react-js-snippets
echo.
pause