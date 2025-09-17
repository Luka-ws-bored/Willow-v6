@echo off
echo Setting up Rust PATH for Tauri development...
set PATH=%PATH%;C:\Users\User\.cargo\bin

echo Current directory: %CD%
cd /d "C:\Users\User\Downloads\Willow v6\willow-tauri\frontend"
echo Changed to: %CD%

echo Testing Rust tools...
cargo --version
echo.

echo Starting Tauri development server...
npm run tauri:dev

pause