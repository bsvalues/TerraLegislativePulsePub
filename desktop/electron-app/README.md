# TerraFusion Executive Desktop App

This directory contains the cross-platform, one-click desktop application for TerraFusion, built with Electron for Windows, macOS, and Linux.

## Features
- One-click build and install (Windows, macOS, Linux)
- Branded installer, auto-updates, and system integration
- Loads the cinematic web splash and full platform in a native window
- Progress bar and status messages throughout the process
- Executive-grade polish and user experience

## How to Build & Install

### **One-Click Build (All Platforms)**
- **Linux/macOS:**
  ```sh
  ./build-desktop.sh
  ```
- **Windows:**
  ```powershell
  ./build-desktop.ps1
  ```
- Installers will be generated in `electron-app/dist/` for your OS.

### **Run the App**
- Double-click the installer for your OS (e.g., `.exe`, `.dmg`, `.AppImage`)
- Follow the branded, step-by-step installer with progress feedback
- App launches automatically after install

## User Experience
- Branded splash and progress window during install and updates
- Clear status messages and error handling
- System tray integration and notifications
- Offline mode supported

## Troubleshooting
- Ensure Node.js and npm are installed
- For Windows, run PowerShell as Administrator if needed
- For macOS, allow apps from identified developers in Security settings
- For Linux, ensure AppImage is executable (`chmod +x`)

## Customization
- Edit `main.js` to change the initial window or add features
- Replace assets in `assets/` for custom branding

For support or enterprise deployment, contact: support@terrafusion.app 