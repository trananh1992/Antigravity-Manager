# ===============================
# Antigravity Manager Build Script
# Windows (EXE / MSI)
# ===============================

Write-Host "=== BUILD ANTIGRAVITY MANAGER (WINDOWS) ==="

# 1. Check node
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js not installed"
    exit 1
}

# 2. Check rust
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Error "Rust not installed"
    exit 1
}

# 3. Install dependencies
Write-Host "Installing dependencies..."
npm install

# 4. Build frontend
Write-Host "Building frontend (Vite)..."
npm run build

# 5. Build Tauri
Write-Host "Building Tauri (EXE / MSI)..."
npm run tauri build

# 6. Result
Write-Host "BUILD DONE"
Write-Host "Artifacts:"
Write-Host "src-tauri\target\release\bundle\msi"
Write-Host "src-tauri\target\release\bundle\nsis"