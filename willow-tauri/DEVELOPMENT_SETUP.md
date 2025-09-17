# 🌲 Willow v6 Complete Development Environment Setup Guide

## 📋 Prerequisites Check

✅ **Node.js**: Already installed (v24.3.0)  
❓ **Rust**: Need to verify/install  
❓ **VSCode**: Need to configure  
❓ **Tauri CLI**: Need to install

## 🚀 Step-by-Step Setup Instructions

### **Step 1: Install Rust** ⚙️

**Option A: Download Installer (Recommended)**

1. Go to https://rustup.rs/
2. Download `rustup-init.exe` for Windows
3. Run the installer
4. Choose **"1) Proceed with installation (default)"**
5. Wait for installation to complete
6. **Restart your Command Prompt/Terminal**

**Option B: PowerShell Command**

```powershell
Invoke-WebRequest -Uri "https://win.rustup.rs/" -OutFile "rustup-init.exe"
.\rustup-init.exe
```

### **Step 2: Verify Rust Installation** ✅

After installation and restarting terminal:

```cmd
rustup --version
cargo --version
rustfmt --version
```

### **Step 3: Install Required Rust Components** 🔧

```cmd
rustup component add rustfmt
```

### **Step 4: Install Tauri CLI Globally** 📦

```cmd
npm install -g @tauri-apps/cli
```

### **Step 5: Install VSCode Extensions** 🔌

**Required Extensions:**

- `rust-lang.rust-analyzer` - Rust language support
- `tauri-apps.tauri-vscode` - Tauri framework support
- `esbenp.prettier-vscode` - Code formatting
- `dsznajder.es7-react-js-snippets` - React development

**Installation Methods:**

1. **Via VSCode Extensions Panel:** Search and install each extension
2. **Via Command Line:**
   ```cmd
   code --install-extension rust-lang.rust-analyzer
   code --install-extension tauri-apps.tauri-vscode
   code --install-extension esbenp.prettier-vscode
   code --install-extension dsznajder.es7-react-js-snippets
   ```

### **Step 6: Open Project in VSCode** 💻

```cmd
cd "c:\Users\User\Downloads\Willow v6\willow-tauri"
code .
```

### **Step 7: Install Frontend Dependencies** 📦

```cmd
cd frontend
npm install
```

### **Step 8: Configure VSCode** ⚙️

**Restart Rust Analyzer:**

1. Press `Ctrl+Shift+P`
2. Type "Rust Analyzer: Restart"
3. Press Enter

**Verify Settings:**

- Go to VSCode Settings (`Ctrl+,`)
- Search "Rust Analyzer: Rustfmt Path"
- Ensure it's **empty** (uses system PATH)

### **Step 9: Test Development Setup** 🧪

```cmd
cd "c:\Users\User\Downloads\Willow v6\willow-tauri\frontend"
npm run tauri:dev
```

**Expected Result:** Tauri window opens with React frontend

## 🛠️ Automated Setup Script

Run the automated setup script:

```cmd
cd "c:\Users\User\Downloads\Willow v6\willow-tauri"
dev_environment_setup.bat
```

## 🐛 Troubleshooting

### **Rust Commands Not Found**

- **Solution:** Restart terminal and VSCode completely
- **Check PATH:** Ensure `C:\Users\%USERNAME%\.cargo\bin` is in system PATH

### **VSCode Rust Analyzer Errors**

- **Solution 1:** `Ctrl+Shift+P` → "Rust Analyzer: Reload Workspace"
- **Solution 2:** `Ctrl+Shift+P` → "Developer: Reload Window"
- **Solution 3:** Ensure you're in directory with `Cargo.toml`

### **"Failed to spawn rustfmt" Error**

- **Solution:** Run `rustup component add rustfmt`

### **Tauri Build Fails**

- **Check:** Node.js version is LTS (✅ already v24.3.0)
- **Check:** Tauri CLI installed globally
- **Check:** In correct `frontend/` directory

### **Python Bridge Issues**

- **Check:** `tauri_bridge.py` exists in parent directory
- **Test:** `python ../tauri_bridge.py --mode status`

## 🎯 Development Workflow

### **Development Mode:**

```cmd
cd frontend
npm run tauri:dev
```

### **Production Build:**

```cmd
cd frontend
npm run tauri:build
```

### **Debug Rust Backend:**

```cmd
cd frontend
cargo tauri dev --debug
```

## 📁 Project Structure Reference

```
willow-tauri/
├── frontend/                # React + Vite frontend
│   ├── src/                # React components
│   ├── src-tauri/          # Rust backend
│   │   ├── src/main.rs     # Tauri commands
│   │   ├── Cargo.toml      # Rust dependencies
│   │   └── tauri.conf.json # Tauri configuration
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js      # Vite configuration
├── tauri_bridge.py         # Python backend bridge
├── .vscode/                # VSCode workspace settings
└── dev_environment_setup.bat # Setup automation
```

## ✅ Setup Completion Checklist

- [ ] Rust installed and in PATH
- [ ] rustfmt component added
- [ ] Tauri CLI installed globally
- [ ] VSCode extensions installed
- [ ] Project opened in VSCode
- [ ] Frontend dependencies installed
- [ ] Rust Analyzer restarted
- [ ] `npm run tauri:dev` works successfully

## 🎉 Success Indicators

When setup is complete, you should see:

- ✅ Tauri window opens with React interface
- ✅ No Rust Analyzer errors in VSCode
- ✅ Hot reload works for React changes
- ✅ Rust compilation works without errors
- ✅ Backend communication through Python bridge functional

Your Willow v6 development environment is now ready for full-stack Tauri + React development! 🚀
