# Willow v6 Tauri Desktop Integration - Complete Setup Guide

## 📋 Overview

This guide provides comprehensive instructions for setting up the Tauri desktop integration for Willow v6. Follow these steps to create a native desktop application that provides a modern GUI interface for all of Willow's AI and RAG capabilities.

## 🎯 What You'll Get

After completing this setup, you'll have:

- A native desktop application for Willow v6
- Modern GUI with chat interface, RAG search, and system monitoring
- Cross-platform compatibility (Windows, macOS, Linux)
- Real-time communication with the Python backend
- Professional-grade desktop app with installers

## 📋 Prerequisites Checklist

Before starting, ensure you have:

### ✅ Core Requirements

- [x] Willow v6 Python backend fully set up and tested
- [x] All RAG features working (if desired)
- [x] Node.js (v16+) installed: https://nodejs.org/
- [x] Rust installed: https://rustup.rs/

### ✅ Platform-Specific Requirements

#### Windows

- [x] Microsoft Visual Studio C++ Build Tools
- [x] WebView2 (pre-installed on Windows 10/11)

#### macOS

- [x] Xcode Command Line Tools: `xcode-select --install`

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install libwebkit2gtk-4.0-dev build-essential curl wget libssl-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev
```

## 🚀 Step-by-Step Setup

### Step 1: Navigate to Project Directory

```bash
cd "c:\Users\User\Downloads\Willow v6\willow-tauri"
```

### Step 2: Verify Willow Backend

Before proceeding, test that your Willow v6 backend is working:

```bash
cd ..
python -m src.main --help  # Should show Willow functionality
python demo_rag_integration.py  # Test RAG if available
```

### Step 3: Install Dependencies

#### Option A: Automatic Setup (Recommended)

**Windows:**

```cmd
setup.bat
```

**macOS/Linux:**

```bash
chmod +x setup.sh
./setup.sh
```

#### Option B: Manual Setup

1. **Install Node.js dependencies:**

   ```bash
   npm install
   ```

2. **Install Tauri CLI:**

   ```bash
   cargo install tauri-cli
   ```

3. **Verify installation:**
   ```bash
   cargo tauri --version
   ```

### Step 4: Create Application Icons (Optional)

For a professional appearance, add icons to the `icons/` directory:

- Place your app icons in `willow-tauri/icons/`
- Required formats: 32x32.png, 128x128.png, icon.ico, icon.icns
- See `icons/README.md` for detailed instructions

### Step 5: Test Development Mode

Run the application in development mode:

```bash
npm run tauri:dev
```

This should:

- Start the Vite development server
- Launch the Tauri desktop application
- Show the Willow Desktop interface
- Connect to the Python backend

### Step 6: Verify Functionality

Test each feature in the desktop app:

1. **Status Tab**: Check that backend connection is green
2. **Chat Tab**: Send a test message to verify LLM integration
3. **RAG Tab**: Perform a document search (if RAG is available)
4. **Settings Tab**: Verify model selection and preferences

## 🏗️ Building for Production

### Development Build

For testing and sharing:

```bash
npm run tauri:build
```

### Release Build

For distribution:

```bash
npm run tauri:build -- --release
```

Build outputs are located in:

- **Windows**: `src-tauri/target/release/bundle/msi/` (installer) and `src-tauri/target/release/` (executable)
- **macOS**: `src-tauri/target/release/bundle/dmg/` (installer) and `src-tauri/target/release/bundle/macos/` (app bundle)
- **Linux**: `src-tauri/target/release/bundle/deb/`, `/rpm/`, `/appimage/` (various package formats)

## ⚙️ Configuration Options

### Tauri Configuration (`tauri.conf.json`)

Key settings you can customize:

```json
{
  "package": {
    "productName": "Willow Desktop",
    "version": "6.0.0"
  },
  "tauri": {
    "windows": [
      {
        "title": "Willow Desktop v6.0.0",
        "width": 1200,
        "height": 800,
        "minWidth": 800,
        "minHeight": 600
      }
    ]
  }
}
```

### Frontend Settings

Users can configure via the Settings tab:

- Default LLM model
- Maximum tokens
- RAG parameters
- Theme preference

Settings are automatically saved to localStorage.

## 🔧 Customization

### Modifying the Interface

- **HTML**: Edit `index.html` for structure changes
- **CSS**: Edit `styles.css` for styling and themes
- **JavaScript**: Edit `app.js` for functionality changes
- **Rust Backend**: Edit `src/main.rs` for Tauri command modifications

### Adding New Features

1. **Frontend**: Add UI elements and JavaScript handlers
2. **Rust Command**: Add new Tauri commands in `src/main.rs`
3. **Python Bridge**: Extend `tauri_bridge.py` with new modes
4. **Backend**: Implement features in the main Willow codebase

### Theme Customization

Edit CSS variables in `styles.css`:

```css
:root {
  --bg-primary: #1a1a1a; /* Main background */
  --text-primary: #ffffff; /* Main text */
  --accent-primary: #4caf50; /* Willow green */
  /* ... more variables */
}
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### Issue: "cargo: command not found"

**Solution**:

1. Install Rust from https://rustup.rs/
2. Restart your terminal
3. Verify: `cargo --version`

#### Issue: "Backend Unavailable" in app

**Solution**:

1. Verify Willow v6 backend works: `python -m src.main`
2. Check bridge script: `python willow-tauri/tauri_bridge.py --mode status`
3. Ensure Python is in PATH

#### Issue: Build fails with "linking with `cc` failed"

**Solution** (Linux):

```bash
sudo apt install build-essential
```

#### Issue: App window doesn't open

**Solution**:

1. Check console for errors
2. Verify WebView2 on Windows
3. Try: `npm run tauri:dev -- --debug`

#### Issue: Frontend changes not reflected

**Solution**:

- Frontend changes: Automatic in dev mode
- Rust changes: Restart `npm run tauri:dev`
- Config changes: Restart development server

### Getting Help

1. **Check the console**: Look for error messages
2. **Test components individually**:
   - Frontend: `npm run dev`
   - Bridge: `python tauri_bridge.py --mode status`
   - Backend: `python -m src.main`
3. **Check file paths**: Ensure all files exist and are accessible
4. **Verify permissions**: Ensure scripts are executable

## 🚀 Distribution

### Creating Installers

The `npm run tauri:build` command creates installers for your platform:

**Windows (.msi)**:

- Professional installer with registry entries
- Start menu shortcuts
- Uninstall support

**macOS (.dmg)**:

- Drag-and-drop installer
- Code signing (if certificates available)
- Notarization support

**Linux (.deb/.rpm/.appimage)**:

- Multiple package formats
- Desktop integration
- System menu entries

### Code Signing (Optional)

For production distribution:

1. Obtain code signing certificates
2. Configure in `tauri.conf.json`
3. Build with signing enabled

## 📈 Performance Optimization

### Build Optimization

- Enable release mode for production: `--release`
- Minimize bundle size by removing unused features
- Optimize icons and assets

### Runtime Performance

- Use async operations for backend communication
- Implement proper error handling and timeouts
- Cache frequently accessed data

## 🔒 Security Considerations

### Tauri Security

- Limited API permissions (configured in `tauri.conf.json`)
- Process isolation between frontend and backend
- Secure communication protocols

### Python Bridge Security

- Input validation and sanitization
- Safe subprocess execution
- Error handling without information leakage

## 📚 Next Steps

After successful setup:

1. **Customize the interface** to match your preferences
2. **Add application icons** for a professional appearance
3. **Test thoroughly** on your target platforms
4. **Create installers** for distribution
5. **Set up code signing** for production releases

## 🤝 Contributing

To contribute improvements:

1. Fork the Willow v6 repository
2. Make changes in the `willow-tauri/` directory
3. Test on multiple platforms if possible
4. Submit pull request with detailed description

## 📖 Additional Resources

- [Tauri Documentation](https://tauri.app/v1/guides/)
- [Rust Book](https://doc.rust-lang.org/book/)
- [Vite Documentation](https://vitejs.dev/guide/)
- [Willow v6 Main Documentation](../README.md)

---

🎉 **Congratulations!** You now have a fully functional desktop application for Willow v6. The native interface provides an excellent user experience while leveraging all of Willow's powerful AI and RAG capabilities.
