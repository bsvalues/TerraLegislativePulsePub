#!/bin/bash
set -e

# TerraFusion One-Click Desktop Build
function print_progress() {
  local msg=$1
  echo -e "\033[1;36m[msg] $msg\033[0m"
}

print_progress "Installing dependencies..."
npm install --prefix desktop/electron-app

print_progress "Building desktop app (all platforms)..."
npm run build --prefix desktop/electron-app

print_progress "Build complete! Installers are in desktop/electron-app/dist/" 