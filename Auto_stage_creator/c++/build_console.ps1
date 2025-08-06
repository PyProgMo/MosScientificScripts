# Simple build script for console version (no GUI dependencies)
# Run this in PowerShell from the project directory

Write-Host "Building Console Version (No GUI dependencies required)" -ForegroundColor Green

# Create build directory
if (!(Test-Path "build_console")) {
    New-Item -ItemType Directory -Name "build_console"
}

# Change to build directory
Set-Location build_console

# Simple compilation without CMake
Write-Host "Compiling with g++ directly..." -ForegroundColor Yellow

# Compile directly
g++ -std=c++17 -o AutoStageConsole.exe ../console_main.cpp ../AutoStageCoordCreator.cpp

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host "Executable created: AutoStageConsole.exe" -ForegroundColor Green
    Write-Host "Run it with: .\AutoStageConsole.exe" -ForegroundColor Yellow
} else {
    Write-Host "Build failed. Trying with Visual Studio compiler..." -ForegroundColor Yellow
    
    # Try with MSVC if g++ is not available
    cl /EHsc /std:c++17 ../console_main.cpp ../AutoStageCoordCreator.cpp /Fe:AutoStageConsole.exe
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Build successful with MSVC!" -ForegroundColor Green
        Write-Host "Executable created: AutoStageConsole.exe" -ForegroundColor Green
    } else {
        Write-Host "Build failed. Make sure you have a C++ compiler installed." -ForegroundColor Red
        Write-Host "Install Visual Studio Build Tools or MinGW-w64" -ForegroundColor Red
    }
}

Set-Location ..
