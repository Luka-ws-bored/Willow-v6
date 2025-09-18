# Launch Willow v6 Desktop - Developer Instructions

1. Ensure .env.local exists (see .env.local.example)
2. Start backend: cd backend; .\.venv\\Scripts\\Activate.ps1; python -m flask run --port 5000
3. Start frontend: cd willow-tauri\\frontend; npm run dev -- --port 1420
4. Start Tauri: cd willow-tauri; $env:TAURI_LOG='debug'; npx tauri dev

If desktop build fails, attach logs from /logs and open PR with artifacts/tauri-rag-debug.zip