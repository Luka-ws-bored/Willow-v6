#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('Verifying Willow v7 UI project setup...\n');

const requiredFiles = [
  'package.json',
  'vite.config.js',
  'tailwind.config.js',
  'postcss.config.js',
  'src/index.css',
  'src/App.jsx',
  'src/lib/willow-tokens.json',
  'src/styles/globals.css',
  'src/variants/framerVariants.js',
  'src/lib/api/models.js',
  'src/lib/api/rag.js',
  'src/components/organisms/NavBar.jsx',
  'src/components/organisms/ModelSwitcher.jsx',
  'src/components/molecules/ChatMessage.jsx',
  'src/screens/MainWorkspace/MainWorkspace.jsx',
  'src/screens/PromptVault/PromptVault.jsx',
  'src/screens/RAGDashboard/RAGDashboard.jsx',
  'tauri.conf.json',
  'willow-components.json',
  'willow-interactions.json',
  'willow-a11y-report.json'
];

const missingFiles = [];

requiredFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (!fs.existsSync(filePath)) {
    missingFiles.push(file);
  }
});

if (missingFiles.length === 0) {
  console.log('✅ All required files are present!');
} else {
  console.log('❌ Missing files:');
  missingFiles.forEach(file => console.log(`  - ${file}`));
}

console.log('\nSetup verification complete.');