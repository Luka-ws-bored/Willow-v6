# chore(tauri): fix tauri config placement and enable desktop dev

## Summary
This PR addresses the Tauri desktop launch issues for Willow on Windows by implementing both Path A (full desktop) and Path B (web-first fallback) approaches. While Path A encountered some configuration and toolchain integration issues, Path B provides a stable web-first development workflow.

## Changes Made

### Path A - Full Desktop (Attempted)
- Installed Rust via rustup with MSVC toolchain
- Installed Visual Studio Build Tools with C++ workload
- Installed Node.js dependencies and Tauri CLI
- Configured tauri.conf.json in the correct locations
- Created normalization script for Tauri config compatibility

### Path B - Web-first Fallback (Implemented)
- Created `scripts/start-dev.bat` to run frontend and backend in parallel
- Documented desktop setup steps and blockers in `docs/desktop-fallback.md`
- Added `TODO_DESKTOP.md` to track remaining desktop build issues

## Files Added
- `scripts/start-dev.bat` - Script to start both frontend and backend servers
- `docs/desktop-fallback.md` - Documentation for desktop setup and blockers
- `TODO_DESKTOP.md` - Tracking file for desktop build issues
- `tools/normalize-tauri-config.js` - Script to normalize Tauri configuration
- `src-tauri/tauri.conf.json` - Tauri configuration file in correct location

## Usage

### Web-first Development
Run the development environment using:
```
.\scripts\start-dev.bat
```

This will start:
- Frontend server at http://localhost:1420
- Backend server at http://localhost:5000

### Desktop Development (WIP)
The desktop setup is partially complete but blocked by:
1. Tauri configuration alignment issues
2. Build toolchain integration challenges
3. PATH resolution for Rust and MSVC tools

Refer to `docs/desktop-fallback.md` for detailed steps to resolve these issues.

## Next Steps
1. Resolve Tauri configuration and toolchain integration issues
2. Test `npx tauri dev` command for successful desktop launch
3. Update documentation once desktop setup is complete