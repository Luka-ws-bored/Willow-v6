@echo off
echo ===============================================
echo Willow Desktop - Build with Icon
echo ===============================================
echo.

REM Check if icon.ico exists
if not exist "icon.ico" (
    echo ERROR: icon.ico file not found!
    echo Please add a proper Windows ICO file named 'icon.ico' in this directory.
    echo Visit https://icoconvert.com/ to convert your PNG to ICO format.
    echo.
    pause
    exit /b 1
)

echo ✓ Found icon.ico file
echo.

echo Cleaning build cache...
cd ..
cargo clean

echo.
echo Starting Tauri development build...
cd ..
npm run tauri:dev

echo.
echo Build complete!
pause