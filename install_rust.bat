@echo off
REM Rust Installation and Verification Script for Willow v6
echo.
echo 🦀 Rust Installation for Willow v6 Development
echo =============================================
echo.

REM Check if Rust is already installed
echo [1/5] Checking current Rust installation...
rustup --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Rust is already installed!
    rustup --version
    cargo --version
    echo.
    goto check_rustfmt
) else (
    echo ❌ Rust not found in PATH
)

echo.
echo [2/5] Running Rust installer...
if exist "rustup-init.exe" (
    echo ✅ Rust installer found, running installation...
    echo Please wait while Rust installs...
    rustup-init.exe -y --default-toolchain stable --profile default
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Installation failed
        pause
        exit /b 1
    )
    echo ✅ Rust installation completed
) else (
    echo ❌ Rust installer not found
    echo Please download from https://rustup.rs/
    pause
    exit /b 1
)

echo.
echo [3/5] Updating PATH and environment...
REM Add Cargo to PATH for this session
set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
echo ✅ PATH updated for this session

echo.
echo [4/5] Verifying Rust installation...
REM Wait a moment for installation to complete
timeout /t 3 >nul

REM Verify installation
"%USERPROFILE%\.cargo\bin\rustup" --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Rust verification failed
    echo Please restart your terminal and try again
    pause
    exit /b 1
)

echo ✅ Rust installed successfully!
"%USERPROFILE%\.cargo\bin\rustup" --version
"%USERPROFILE%\.cargo\bin\cargo" --version

:check_rustfmt
echo.
echo [5/5] Installing rustfmt component...
"%USERPROFILE%\.cargo\bin\rustup" component list --installed | findstr "rustfmt" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing rustfmt component...
    "%USERPROFILE%\.cargo\bin\rustup" component add rustfmt
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to install rustfmt
        pause
        exit /b 1
    )
    echo ✅ rustfmt installed
) else (
    echo ✅ rustfmt already installed
)

echo.
echo 🎉 Rust installation complete!
echo.
echo Next steps:
echo 1. **RESTART YOUR TERMINAL** - This is required for PATH changes
echo 2. Verify installation: rustup --version
echo 3. Install Tauri CLI: npm install -g @tauri-apps/cli
echo 4. Navigate to frontend: cd willow-tauri\frontend
echo 5. Start development: npm run tauri:dev
echo.
echo ⚠️  IMPORTANT: You must restart your terminal before Rust commands will work!
echo.
pause