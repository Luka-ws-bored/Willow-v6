#!/bin/bash
# Willow Desktop Setup Script for macOS/Linux

set -e

echo ""
echo "🌲 Willow Desktop v6.0.0 Setup"
echo "================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first:"
    echo "   https://nodejs.org/"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not available. Please install Node.js with npm."
    exit 1
fi

echo "✅ Node.js found"
node --version

# Install frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
npm install

echo "✅ Frontend dependencies installed"

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo ""
    echo "⚠️  Rust is not installed. To complete the setup:"
    echo ""
    echo "1. Install Rust from: https://rustup.rs/"
    echo "2. Restart your terminal"
    echo "3. Run this script again or manually install Tauri CLI:"
    echo "   cargo install tauri-cli"
    echo ""
    echo "Frontend is ready, but you'll need Rust for building the desktop app."
    exit 0
fi

echo "✅ Rust found"
cargo --version

# Install Tauri CLI
echo ""
echo "🔧 Installing Tauri CLI..."
cargo install tauri-cli --version "^1.4"

echo "✅ Tauri CLI installed"

echo ""
echo "🎉 Setup complete! You can now:"
echo ""
echo "  • Run in development mode: npm run tauri:dev"
echo "  • Build for production: npm run tauri:build"
echo "  • Test frontend only: npm run dev"
echo ""
echo "📚 Make sure the Willow v6 Python backend is available in the parent directory."
echo ""