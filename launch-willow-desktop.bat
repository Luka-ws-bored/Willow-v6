@echo off
echo ===============================================
echo   Willow v6 Tauri Development Environment
echo ===============================================
echo.

echo Step 1: Setting up environment...
set PATH=%PATH%;C:\Users\User\.cargo\bin

echo Step 2: Navigating to frontend directory...
pushd "C:\Users\User\Downloads\Willow v6\willow-tauri\frontend"
echo Current directory: %CD%

echo Step 3: Verifying Rust installation...
cargo --version
if errorlevel 1 (
    echo ERROR: Cargo not found in PATH
    echo Please ensure Rust is properly installed
    pause
    exit /b 1
)

echo Step 4: Verifying Node.js installation...
npm --version
if errorlevel 1 (
    echo ERROR: npm not found
    echo Please ensure Node.js is properly installed
    pause
    exit /b 1
)

echo Step 5: Checking package.json...
if not exist package.json (
    echo ERROR: package.json not found in current directory
    echo Current directory: %CD%
    dir
    pause
    exit /b 1
)

echo Step 6: Starting Tauri development server...
echo This will launch the Willow v6 desktop application
echo.
npm run tauri:dev

popd
pause