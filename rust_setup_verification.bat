@echo off
echo.
echo 🦀 Rust + Tauri Development Environment Setup Verification
echo =========================================================
echo.

REM Check Rust installation
echo Checking Rust installation...
rustup --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Rust not found. Please install from https://rustup.rs/
    pause
    exit /b 1
)

echo ✅ Rust found
echo.

REM Check Cargo
echo Checking Cargo...
cargo --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Cargo not found
    pause
    exit /b 1
)

echo ✅ Cargo found
echo.

REM Check installed components
echo Checking installed Rust components...
rustup component list --installed

REM Check if rustfmt is installed
rustup component list --installed | findstr "rustfmt" >nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️ rustfmt not found. Installing...
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

REM Check rustfmt version
echo.
echo Checking rustfmt version...
rustfmt --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ rustfmt not working properly
    pause
    exit /b 1
)

echo ✅ rustfmt working
echo.

REM Check if in correct directory
cd /d "c:\Users\User\Downloads\Willow v6\willow-tauri\frontend"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Could not navigate to Tauri frontend directory
    pause
    exit /b 1
)

echo ✅ In Tauri frontend directory
echo Current directory: %CD%
echo.

REM Check Tauri CLI
echo Checking Tauri CLI...
where cargo >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    cargo tauri --version >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo ⚠️ Tauri CLI not found. You can install it with:
        echo    cargo install tauri-cli
        echo.
    ) else (
        echo ✅ Tauri CLI found
        cargo tauri --version
        echo.
    )
)

echo 🎉 Rust environment verification complete!
echo.
echo Next steps:
echo 1. Install VSCode Rust Analyzer extension if not already installed
echo 2. Open this project in VSCode
echo 3. Run 'npm run tauri:dev' to start development
echo.
pause