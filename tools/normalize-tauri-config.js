// created by Qoder - normalizes certain v2->v1 tauri keys
const fs = require('fs');
const p = './src-tauri/tauri.conf.json';
if (!fs.existsSync(p)) { console.error('no config at', p); process.exit(1); }
const cfg = JSON.parse(fs.readFileSync(p,'utf8'));
let changed=false;
if (cfg.build && (cfg.build.devUrl || cfg.build.frontendDist)) { cfg.build.devPath = cfg.build.devPath || cfg.build.devUrl; cfg.build.distDir = cfg.build.distDir || cfg.build.frontendDist; delete cfg.build.devUrl; delete cfg.build.frontendDist; changed=true; }
if (cfg.app) { cfg.package = cfg.package || {}; if (cfg.app.productName) cfg.package.productName = cfg.package.productName || cfg.app.productName; if (cfg.app.version) cfg.package.version = cfg.package.version || cfg.app.version; delete cfg.app; changed=true; }
if (cfg.identifier) { cfg.tauri = cfg.tauri || {}; cfg.tauri.bundle = cfg.tauri.bundle || {}; cfg.tauri.bundle.identifier = cfg.tauri.bundle.identifier || cfg.identifier; delete cfg.identifier; changed=true; }
if (changed) fs.writeFileSync(p, JSON.stringify(cfg,null,2)); console.log(changed? 'normalized tauri config':'no change');
