@echo off
REM Willow v6 Complete Development Environment Setup Script
echo.
echo 🌲 Willow v6 Development Environment Setup
echo ==========================================
echo.

REM Step 1: Check Node.js (already installed)
echo [1/10] Checking Node.js installation...
node --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js not found. Please install from https://nodejs.org/
    pause
    exit /b 1
) else (
    echo ✅ Node.js found:
    node --version
    npm --version
)
echo.

REM Step 2: Check Rust installation
echo [2/10] Checking Rust installation...
rustup --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Rust not found. 
    echo.
    echo Please install Rust:
    echo 1. Go to https://rustup.rs/
    echo 2. Download rustup-init.exe
    echo 3. Run installer with default settings
    echo.
    echo Alternative PowerShell command:
    echo Invoke-WebRequest -Uri "https://win.rustup.rs/" -OutFile "rustup-init.exe" ; .\rustup-init.exe
    echo.
    echo After installation, restart this script.
    pause
    exit /b 1
) else (
    echo ✅ Rust found:
    rustup --version
    cargo --version
)
echo.

REM Step 3: Check and install rustfmt
echo [3/10] Checking rustfmt component...
rustup component list --installed | findstr "rustfmt" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Installing rustfmt...
    rustup component add rustfmt
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to install rustfmt
        pause
        exit /b 1
    )
    echo ✅ rustfmt installed
) else (
    echo ✅ rustfmt already installed
)
rustfmt --version
echo.

REM Step 4: Install Tauri CLI globally
echo [4/10] Installing Tauri CLI...
npm list -g @tauri-apps/cli >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing Tauri CLI globally...
    npm install -g @tauri-apps/cli
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to install Tauri CLI
        pause
        exit /b 1
    )
    echo ✅ Tauri CLI installed
) else (
    echo ✅ Tauri CLI already installed
)
echo.

REM Step 5: Navigate to frontend directory
echo [5/10] Navigating to frontend directory...
cd /d "c:\Users\User\Downloads\Willow v6\willow-tauri\frontend"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Could not find frontend directory
    pause
    exit /b 1
)
echo ✅ In frontend directory: %CD%
echo.

REM Step 6: Install frontend dependencies
echo [6/10] Installing frontend dependencies...
if not exist "package.json" (
    echo ❌ package.json not found in frontend directory
    pause
    exit /b 1
)

npm install
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)
echo ✅ Frontend dependencies installed
echo.

REM Step 7: Verify Tauri setup
echo [7/10] Verifying Tauri setup...
npm run tauri --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Tauri CLI not working from project. This is normal on first setup.
) else (
    echo ✅ Tauri CLI working from project
    npm run tauri --version
)
echo.

REM Step 8: Check Python bridge
echo [8/10] Checking Python bridge...
if exist "..\tauri_bridge.py" (
    echo ✅ Python bridge found
) else (
    echo ⚠️ Python bridge not found - this may cause backend communication issues
)
echo.

REM Step 9: Check VSCode workspace configuration
echo [9/10] Checking VSCode workspace...
if exist "..\.vscode\settings.json" (
    echo ✅ VSCode settings configured
) else (
    echo ⚠️ VSCode settings not found - extension configuration may be needed
)
echo.

REM Step 10: Final verification
echo [10/10] Environment setup complete!
echo.
echo 🎉 Development Environment Summary:
echo ✅ Node.js: Installed and working
echo ✅ Rust: Installed and working
echo ✅ rustfmt: Installed
echo ✅ Tauri CLI: Installed globally  
echo ✅ Frontend dependencies: Installed
echo.
echo 📝 Next Steps:
echo 1. Install VSCode extensions:
echo    - rust-lang.rust-analyzer
echo    - tauri-apps.tauri-vscode
echo    - esbenp.prettier-vscode
echo    - dsznajder.es7-react-js-snippets
echo.
echo 2. Open project in VSCode:
echo    code "c:\Users\User\Downloads\Willow v6\willow-tauri"
echo.
echo 3. Start development:
echo    npm run tauri:dev
echo.
echo 4. If you encounter issues:
echo    - Restart VSCode after installing extensions
echo    - Run 'Rust Analyzer: Restart' in Command Palette
echo    - Ensure you're in the frontend directory for npm commands
echo.
pause