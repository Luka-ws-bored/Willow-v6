import { execSync } from 'child_process';
import { readFileSync, existsSync } from 'fs';

console.log('Verifying Willow v7 fixes...');

// Check if Tauri config is correct
try {
  const tauriConfig = JSON.parse(readFileSync('tauri.conf.json', 'utf8'));
  if (tauriConfig.build && tauriConfig.build.devUrl) {
    console.log('✅ Tauri configuration is correct');
  } else {
    console.log('❌ Tauri configuration needs fixing');
  }
} catch (e) {
  console.log('❌ Tauri configuration file error:', e.message);
}

// Check if dependencies are installed
try {
  const packageJson = JSON.parse(readFileSync('package.json', 'utf8'));
  if (existsSync('node_modules')) {
    console.log('✅ Dependencies are installed');
  } else {
    console.log('❌ Dependencies are missing');
  }
} catch (e) {
  console.log('❌ Error checking dependencies:', e.message);
}

console.log('Fix verification completed');