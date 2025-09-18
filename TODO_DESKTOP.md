# TODO: Desktop Build Setup

The desktop build for Willow is currently blocked by missing Rust/MSVC toolchain integration.

## Current Status

- [x] Rust installed via rustup
- [x] Visual Studio Build Tools installed
- [x] Node.js and npm available
- [x] Tauri CLI installed
- [ ] Tauri configuration properly aligned
- [ ] Build toolchain integration working
- [ ] `npx tauri dev` successfully launching desktop app

## Blockers

1. **Tauri Configuration**: The tauri.conf.json file location and structure need to be verified for compatibility with the current project structure.
2. **Build Toolchain**: Integration between Rust MSVC toolchain and Visual Studio Build Tools needs to be confirmed.
3. **Path Resolution**: PATH variables for Rust and MSVC tools may need adjustment.

## Next Steps

1. Review the detailed steps in [docs/desktop-fallback.md](docs/desktop-fallback.md)
2. Verify tauri.conf.json location and structure
3. Confirm PATH variables for Rust and MSVC tools
4. Test `npx tauri dev` command again

## Temporary Workaround

Use the web-first approach with `scripts/start-dev.bat` to run both frontend and backend servers in parallel.

- Frontend: http://localhost:1420
- Backend: http://localhost:5000