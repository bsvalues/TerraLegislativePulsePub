# TerraFusion One-Click Desktop Build

function Print-Progress($msg) {
    Write-Host "[msg] $msg" -ForegroundColor Cyan
}

Print-Progress "Installing dependencies..."
npm install --prefix desktop/electron-app

Print-Progress "Building desktop app (all platforms)..."
npm run build --prefix desktop/electron-app

Print-Progress "Build complete! Installers are in desktop/electron-app/dist/" 