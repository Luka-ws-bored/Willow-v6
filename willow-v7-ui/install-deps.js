#!/usr/bin/env node

import { execSync } from 'child_process';
import { existsSync } from 'fs';

console.log('Installing Willow v7 dependencies...');

try {
  // Check if npm is available
  execSync('npm --version', { stdio: 'pipe' });
  console.log('✅ npm is available');
} catch (e) {
  console.log('❌ npm is not available. Please install Node.js and npm.');
  process.exit(1);
}

try {
  // Install dependencies
  console.log('Installing npm dependencies...');
  execSync('npm install', { stdio: 'inherit' });
  console.log('✅ npm dependencies installed');
} catch (e) {
  console.log('❌ Failed to install npm dependencies:', e.message);
  process.exit(1);
}

console.log('All dependencies installed successfully!');