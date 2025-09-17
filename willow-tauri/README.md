# Willow Desktop v6.0.0 - Tauri Integration

A native desktop application for Willow v6 built with Tauri, providing a modern GUI interface for all Willow's AI and RAG capabilities.

## 🌟 Features

- **🖥️ Native Desktop App**: Cross-platform desktop application (Windows, macOS, Linux)
- **💬 Interactive Chat**: Real-time chat interface with Willow's LLM capabilities
- **📚 RAG Interface**: Intuitive document search and retrieval interface
- **⚙️ Settings Management**: Easy configuration of models, parameters, and preferences
- **📊 System Status**: Real-time monitoring of backend capabilities and performance
- **🎨 Modern UI**: Clean, responsive interface with dark/light theme support
- **🔄 Live Updates**: Real-time status updates and capability detection

## 📋 Prerequisites

Before setting up the Tauri desktop integration, ensure you have:

### Required Software

1. **Node.js** (v16 or higher)

   - Download from: https://nodejs.org/
   - Verify installation: `node --version`

2. **Rust** (latest stable)

   - Install from: https://rustup.rs/
   - Verify installation: `cargo --version`

3. **Willow v6 Backend**
   - Ensure the parent Willow v6 project is set up and functional
   - All RAG dependencies should be installed if you want full functionality

### System Dependencies (Platform-specific)

#### Windows

- Microsoft Visual Studio C++ Build Tools
- WebView2 (usually pre-installed on Windows 10/11)

#### macOS

- Xcode Command Line Tools: `xcode-select --install`

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install libwebkit2gtk-4.0-dev \
    build-essential \
    curl \
    wget \
    libssl-dev \
    libgtk-3-dev \
    libayatana-appindicator3-dev \
    librsvg2-dev
```

## 🚀 Quick Setup

### Step 1: Navigate to the Tauri Directory

```bash
cd "c:\Users\User\Downloads\Willow v6\willow-tauri"
```

### Step 2: Run Setup Script

#### Windows

```cmd
setup.bat
```

#### macOS/Linux

```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:

- Install Node.js dependencies
- Install Tauri CLI
- Verify all prerequisites
- Provide next steps

## 🔧 Development

### Run in Development Mode

```bash
npm run tauri:dev
```

This will:

- Start the Vite development server
- Launch the Tauri application
- Enable hot-reloading for frontend changes
- Provide debugging capabilities

### Frontend Only Development

```bash
npm run dev
```

Opens the frontend in a web browser for UI development and testing.

### Available Scripts

```bash
npm run dev          # Start Vite dev server
npm run build        # Build frontend for production
npm run tauri:dev    # Run Tauri in development mode
npm run tauri:build  # Build production desktop app
npm run preview      # Preview production build
```

## 🏗️ Building for Production

### Build Desktop Application

```bash
npm run tauri:build
```

This creates platform-specific installers in `src-tauri/target/release/bundle/`:

- **Windows**: `.msi` installer and `.exe` executable
- **macOS**: `.dmg` installer and `.app` bundle
- **Linux**: `.deb`, `.rpm` packages and `.appimage`

### Build Configuration

The build process is configured in `tauri.conf.json`:

- App metadata and version
- Bundle settings and icons
- Security permissions
- Window configuration

## 📁 Project Structure

```
willow-tauri/
├── src/
│   └── main.rs              # Rust backend with Tauri commands
├── src-tauri/
│   ├── Cargo.toml           # Rust dependencies
│   ├── tauri.conf.json      # Tauri configuration
│   └── build.rs             # Build script
├── index.html               # Main HTML interface
├── styles.css               # Application styles
├── app.js                   # Frontend JavaScript logic
├── tauri_bridge.py          # Python bridge script
├── package.json             # Node.js dependencies
├── vite.config.js           # Vite configuration
├── setup.bat               # Windows setup script
├── setup.sh                # Unix setup script
└── README.md               # This file
```

## 🔌 Architecture

### Frontend (HTML/CSS/JavaScript)

- **Vite**: Modern build tool and development server
- **Vanilla JavaScript**: No framework dependencies for maximum performance
- **CSS Variables**: Themeable design system
- **Responsive Design**: Adaptable to different window sizes

### Backend Bridge (Rust + Python)

- **Tauri Commands**: Rust functions exposed to frontend
- **Python Bridge**: CLI interface to Willow v6 backend
- **Process Management**: Secure subprocess execution
- **Error Handling**: Comprehensive error reporting

### Communication Flow

```
Frontend JS → Tauri Commands → Python Bridge → Willow Backend
                ↓
            JSON Response ← JSON Response ← JSON Response
```

## 🛠️ Configuration

### Tauri Configuration (`tauri.conf.json`)

Key settings you can modify:

- `windows`: Window size, title, and behavior
- `allowlist`: API permissions for security
- `bundle`: App metadata and icon paths
- `security`: Content Security Policy settings

### Frontend Settings

User preferences are stored in localStorage:

- Default LLM model
- Token limits
- RAG parameters
- Theme selection

## 🔒 Security

The desktop application implements several security measures:

- **Restricted API Access**: Only necessary Tauri APIs are enabled
- **Path Validation**: Secure file system access
- **Process Isolation**: Python backend runs in separate process
- **Content Security**: CSP headers and input validation

## 🎨 Theming

The application supports both dark and light themes:

- **Dark Theme**: Default, optimized for extended use
- **Light Theme**: Available via settings
- **CSS Variables**: Easy customization of colors and styling
- **System Integration**: Respects OS theme preferences

## 📊 Features Overview

### Chat Interface

- Real-time conversation with Willow's LLM capabilities
- Model selection and parameter configuration
- Message history and timestamps
- Error handling and status indicators

### RAG Search

- Document search interface
- Custom document input or default knowledge base
- Configurable result count (top-k)
- Source citation and context display

### System Status

- Real-time backend connectivity monitoring
- Capability detection and feature availability
- Model listing and performance metrics
- Comprehensive system information

### Settings Management

- LLM model defaults and preferences
- RAG configuration parameters
- Theme selection and UI preferences
- Persistent settings storage

## 🐛 Troubleshooting

### Common Issues

#### "cargo not found" Error

- Install Rust from https://rustup.rs/
- Restart your terminal/IDE
- Verify installation: `cargo --version`

#### "Python script not found" Error

- Ensure `tauri_bridge.py` exists in the `willow-tauri` directory
- Verify Python is installed and accessible
- Check that the parent Willow v6 directory exists

#### Frontend Shows "Backend Unavailable"

- Verify the Willow v6 backend is properly installed
- Check that Python dependencies are installed
- Test the bridge script manually: `python tauri_bridge.py --mode status`

#### Build Fails on Linux

- Install required system dependencies (see Prerequisites)
- Update Rust: `rustup update`
- Clear Cargo cache: `cargo clean`

### Development Tips

1. **Hot Reload**: Frontend changes reload automatically in dev mode
2. **Rust Changes**: Require restarting `npm run tauri:dev`
3. **Debugging**: Use browser dev tools in Tauri dev mode
4. **Logs**: Check console output for backend communication errors

## 🤝 Contributing

To contribute to the Tauri integration:

1. Make changes to the appropriate files:

   - Frontend: `index.html`, `styles.css`, `app.js`
   - Backend: `src/main.rs`
   - Bridge: `tauri_bridge.py`
   - Config: `tauri.conf.json`, `Cargo.toml`

2. Test in development mode: `npm run tauri:dev`

3. Verify production build: `npm run tauri:build`

4. Submit pull request with comprehensive testing

## 📜 License

This Tauri integration is part of Willow v6 and is licensed under the MIT License.

## 🔗 Links

- [Willow v6 Main Repository](https://github.com/Luka-ws-bored/Willow-v6)
- [Tauri Documentation](https://tauri.app/)
- [Vite Documentation](https://vitejs.dev/)
- [Rust Documentation](https://doc.rust-lang.org/)

---

**Willow Desktop v6.0.0** - Native AI-powered desktop application
