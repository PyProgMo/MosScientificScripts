# Comprehensive build script for Windows
# This script will try multiple approaches to build the project

Write-Host "AutoStage Coordinate Creator - Build Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Function to test if a command exists
function Test-Command($cmdname) {
    try {
        if (Get-Command $cmdname -ErrorAction Stop) { return $true }
    }
    catch { return $false }
}

# Check for Visual Studio Developer Command Prompt
$vsPath = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"
$vsPath2022 = "${env:ProgramFiles}\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
$vsBuildTools = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
$vsBuildTools2022 = "${env:ProgramFiles}\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"

Write-Host "`nChecking available compilers..." -ForegroundColor Yellow

# Check for compilers
$hasGcc = Test-Command "g++"
$hasCl = Test-Command "cl"
$hasCmake = Test-Command "cmake"
$hasVcpkg = Test-Command "vcpkg"

Write-Host "GCC (g++): $hasGcc" -ForegroundColor $(if($hasGcc){"Green"}else{"Red"})
Write-Host "MSVC (cl): $hasCl" -ForegroundColor $(if($hasCl){"Green"}else{"Red"})
Write-Host "CMake: $hasCmake" -ForegroundColor $(if($hasCmake){"Green"}else{"Red"})
Write-Host "vcpkg: $hasVcpkg" -ForegroundColor $(if($hasVcpkg){"Green"}else{"Red"})

# Try to find Visual Studio installations
$vsInstallations = @()
if (Test-Path $vsPath) { $vsInstallations += $vsPath }
if (Test-Path $vsPath2022) { $vsInstallations += $vsPath2022 }
if (Test-Path $vsBuildTools) { $vsInstallations += $vsBuildTools }
if (Test-Path $vsBuildTools2022) { $vsInstallations += $vsBuildTools2022 }

if ($vsInstallations.Count -gt 0) {
    Write-Host "Found Visual Studio installations:" -ForegroundColor Green
    $vsInstallations | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
}

Write-Host "`n" -ForegroundColor White

# Strategy 1: Try with existing tools
if ($hasGcc -and $hasCmake) {
    Write-Host "Strategy 1: Using GCC + CMake" -ForegroundColor Green
    try {
        if (!(Test-Path "build")) { New-Item -ItemType Directory -Name "build" }
        Set-Location build
        cmake -G "MinGW Makefiles" ..
        cmake --build .
        Set-Location ..
        Write-Host "Build successful with GCC!" -ForegroundColor Green
        exit 0
    } catch {
        Write-Host "GCC build failed: $($_.Exception.Message)" -ForegroundColor Red
        Set-Location ..
    }
}

# Strategy 2: Try with Visual Studio if available
if ($vsInstallations.Count -gt 0) {
    Write-Host "Strategy 2: Using Visual Studio" -ForegroundColor Green
    $vsPath = $vsInstallations[0]
    
    # Create a batch file to call VS tools and compile
    $batchContent = @"
@echo off
call "$vsPath"
cd /d "%~dp0"
if not exist build_vs mkdir build_vs
cd build_vs
cl /EHsc /std:c++17 /I. ..\console_main.cpp ..\AutoStageCoordCreator.cpp /Fe:AutoStageConsole.exe
if %ERRORLEVEL% EQU 0 (
    echo Build successful with Visual Studio!
    echo Executable: build_vs\AutoStageConsole.exe
) else (
    echo Build failed with Visual Studio
)
pause
"@
    
    $batchContent | Out-File -FilePath "compile_vs.bat" -Encoding ASCII
    Write-Host "Created compile_vs.bat - run this to compile with Visual Studio tools" -ForegroundColor Yellow
}

# Strategy 3: Manual compilation instructions
Write-Host "`nManual Compilation Instructions:" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Yellow
Write-Host "Option 1: Install Visual Studio Community (free)" -ForegroundColor White
Write-Host "  Download from: https://visualstudio.microsoft.com/vs/community/" -ForegroundColor Gray
Write-Host "  Make sure to install C++ build tools" -ForegroundColor Gray

Write-Host "`nOption 2: Install MinGW-w64" -ForegroundColor White
Write-Host "  Download from: https://www.mingw-w64.org/downloads/" -ForegroundColor Gray
Write-Host "  Or use chocolatey: choco install mingw" -ForegroundColor Gray

Write-Host "`nOption 3: Use online compiler" -ForegroundColor White
Write-Host "  Copy the source files to: https://replit.com/ or https://godbolt.org/" -ForegroundColor Gray

Write-Host "`nFor now, you can also test the Python version to verify the algorithm works." -ForegroundColor Cyan
