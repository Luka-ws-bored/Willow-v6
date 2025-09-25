#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');

console.log('Initializing Tauri...');

try {
  // Check if Tauri CLI is installed
  execSync('npx tauri --version', { stdio: 'ignore' });
  console.log('Tauri CLI is already installed.');
} catch (error) {
  console.log('Installing Tauri CLI...');
  execSync('npm install -g @tauri-apps/cli', { stdio: 'inherit' });
}

// Initialize Tauri
console.log('Setting up Tauri app...');
execSync('npx tauri init', { stdio: 'inherit' });

console.log('Tauri initialization complete!');
console.log('To run the app in development mode, use: npm run tauri dev');
console.log('To build the app, use: npm run tauri build');