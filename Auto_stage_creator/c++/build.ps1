# Build script for Windows
# Run this in PowerShell from the project directory

# Create build directory
if (!(Test-Path "build")) {
    New-Item -ItemType Directory -Name "build"
}

# Change to build directory
Set-Location build

# Configure with CMake
cmake ..

# Build the project
cmake --build . --config Release

# Inform user
Write-Host "Build complete! Executable should be in build/bin/ or build/Release/"
Write-Host "If Tcl/Tk is not found, make sure it's installed and in your PATH."
Write-Host "You can install Tcl/Tk from: https://www.tcl.tk/software/tcltk/download.html"
