#!/bin/bash
set -e

echo "=== BUILD ANTIGRAVITY MANAGER (MACOS) ==="

# 1. Check node
if ! command -v node &> /dev/null; then
  echo "Node.js not installed"
  exit 1
fi

# 2. Check rust
if ! command -v cargo &> /dev/null; then
  echo "Rust not installed"
  exit 1
fi

# 3. Install deps
echo "Installing dependencies..."
npm install

# 4. Build frontend
echo "Building frontend (Vite)..."
npm run build

# 5. Build tauri
echo "Building Tauri (.app / .dmg)..."
npm run tauri build

echo "BUILD DONE"
echo "Artifacts:"
echo "src-tauri/target/release/bundle/dmg"