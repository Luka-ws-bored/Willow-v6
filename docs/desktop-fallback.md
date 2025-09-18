# Desktop Fallback: Web-first Development Setup

This document describes the steps required to run Willow in desktop mode and the blockers encountered during setup.

## Path A - Full Desktop Setup (Recommended but Blocked)

### A1. Install Rust (via rustup) and ensure MSVC toolchain

```powershell
# Install rustup (non-interactive) if not present
if (-not (Get-Command rustup -ErrorAction SilentlyContinue)) {
  Invoke-WebRequest -Uri https://win.rustup.rs -OutFile .\rustup-init.exe
  .\rustup-init.exe -y
}
# Ensure default toolchain is stable-msvc
rustup default stable-x86_64-pc-windows-msvc
rustup update
```

### A2. Install Visual Studio Build Tools (if missing)

Tauri requires the C/C++ build toolchain. Use Chocolatey if available.

```powershell
if (-not (Get-Command cl.exe -ErrorAction SilentlyContinue)) {
  choco install visualstudio2022buildtools -y --package-parameters "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --quiet"
}
```

If Chocolatey is not present, run the Visual Studio Build Tools installer manually and include "Desktop development with C++" workload.

### A3. Ensure Node tooling & Tauri CLI is installed in project

```powershell
# from project root
# use project's package manager (if package-lock.json exists assume npm)
if (Test-Path package-lock.json) { npm ci } else { npm i }
# Install / update local tauri CLI to match project expectations
npm install --save-dev @tauri-apps/cli@latest
```

### A4. Detect and fix tauri config location & schema

1. Locate `tauri.conf.json` candidates:

```powershell
Get-ChildItem -Path . -Recurse -Filter "tauri.conf.json" -ErrorAction SilentlyContinue | Select-Object FullName
Get-ChildItem -Path . -Recurse -Include "tauri.conf.json*" | Select-Object FullName
```

2. The canonical location for many Tauri projects is `src-tauri/tauri.conf.json`. If the file exists elsewhere (e.g., `willow-tauri/tauri.conf.json` or project root), move/copy it to `src-tauri`:

```powershell
# ensure src-tauri exists
if (-not (Test-Path .\src-tauri)) { mkdir src-tauri }
# copy the most likely file if src-tauri missing
if (Test-Path .\willow-tauri\tauri.conf.json -and -not (Test-Path .\src-tauri\tauri.conf.json)) { cp .\willow-tauri\tauri.conf.json .\src-tauri\tauri.conf.json }
if (Test-Path .\tauri.conf.json -and -not (Test-Path .\src-tauri\tauri.conf.json)) { cp .\tauri.conf.json .\src-tauri\tauri.conf.json }
```

3. Normalize schema: if CLI complains about unexpected keys (e.g., `devUrl`, `frontendDist`, `app` at top-level), transform the v2-style keys to v1-style expected by many `@tauri-apps/cli` versions. Create a small Node script `tools/normalize-tauri-config.js` and run it.

4. Validate config by running the CLI config-check:

```powershell
npx tauri dev --config-check
# or just run tauri dev to see errors
```

### A5. Run Tauri in dev mode (build & dev)

```powershell
# ensure frontend dev server is running on devPath (http://localhost:1420)
npx tauri dev
```

## Current Blockers

1. **Tauri Configuration Issues**: The Tauri configuration file location and structure may need adjustment for the current project setup.
2. **Build Toolchain Integration**: Ensuring the Rust MSVC toolchain integrates properly with the Visual Studio Build Tools.
3. **Path Resolution**: Correctly setting up PATH variables for both Rust and MSVC tools.

## Path B - Web-first Fallback (Currently Working)

Use the provided `scripts/start-dev.bat` to run both frontend and backend servers in parallel.

### Usage

1. Run the start-dev.bat script:
   ```
   .\scripts\start-dev.bat
   ```

2. Access the services:
   - Frontend: http://localhost:1420
   - Backend: http://localhost:5000

This approach allows for continued development while the desktop setup issues are resolved.