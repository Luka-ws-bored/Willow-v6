Start-Process -FilePath powershell -ArgumentList '-NoExit','-Command','cd ./backend; .\.venv\\Scripts\\Activate.ps1; python -m flask run --port 5000' -WindowStyle Normal
Start-Process -FilePath powershell -ArgumentList '-NoExit','-Command','cd ./willow-tauri\\frontend; npm run dev -- --port 1420' -WindowStyle Normal
Start-Sleep -s 6
cd ./willow-tauri
$env:TAURI_LOG='debug'
npx tauri dev 2>&1 | Tee-Object -FilePath ..\\logs\\tauri_dev_final.log