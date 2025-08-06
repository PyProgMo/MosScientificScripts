# Try to build Tcl/Tk GUI with different approaches
# This script will try multiple methods to get Tcl/Tk working

Write-Host "Building Tcl/Tk GUI Version" -ForegroundColor Cyan

# Method 1: Try with pre-installed ActiveTcl
$activeTclPaths = @(
    "C:\Tcl",
    "C:\ActiveTcl",
    "C:\Program Files\Tcl",
    "C:\Program Files (x86)\Tcl"
)

$tclFound = $false
$tclPath = ""

foreach ($path in $activeTclPaths) {
    if (Test-Path "$path\include\tcl.h") {
        $tclPath = $path
        $tclFound = $true
        Write-Host "Found Tcl/Tk at: $path" -ForegroundColor Green
        break
    }
}

if ($tclFound) {
    # Build with found Tcl/Tk installation
    $tcltkBatch = @"
@echo off
echo Building with Tcl/Tk from $tclPath
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cd /d "%~dp0"

if not exist build_tclgui mkdir build_tclgui
cd build_tclgui

cl /EHsc /std:c++17 /I"$tclPath\include" ..\main.cpp ..\AutoStageCoordCreator.cpp ..\AutoStageGUI.cpp /link "$tclPath\lib\tcl90.lib" "$tclPath\lib\tk90.lib" /Fe:AutoStageTclGUI.exe

if %ERRORLEVEL% EQU 0 (
    echo Tcl/Tk GUI build successful!
    echo Executable: build_tclgui\AutoStageTclGUI.exe
    echo Starting the Tcl/Tk GUI...
    set PATH=$tclPath\bin;%PATH%
    AutoStageTclGUI.exe
) else (
    echo Tcl/Tk GUI build failed
)
pause
"@
    
    $tcltkBatch | Out-File -FilePath "compile_tclgui.bat" -Encoding ASCII
    Write-Host "Created compile_tclgui.bat for Tcl/Tk GUI" -ForegroundColor Green
    Write-Host "Run this to build and start the Tcl/Tk GUI" -ForegroundColor Yellow
    
} else {
    Write-Host "No Tcl/Tk installation found in standard locations" -ForegroundColor Red
    Write-Host "Please install ActiveTcl from: https://www.tcl.tk/software/tcltk/download.html" -ForegroundColor Yellow
    Write-Host "Or use the Windows native GUI version which is already working" -ForegroundColor Green
}

Write-Host "`nAlternative: The Windows native GUI is already working perfectly!" -ForegroundColor Cyan
Write-Host "Location: build_wingui\AutoStageGUI.exe" -ForegroundColor Green
