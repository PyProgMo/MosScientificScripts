# Script to compile Tk and then build the GUI version
# Run this after the console version is working

Write-Host "Compiling Tk from C:/dev/tk9.0.2" -ForegroundColor Cyan

# First, let's check if Tk source exists
if (Test-Path "C:/dev/tk9.0.2") {
    Write-Host "Found Tk source directory" -ForegroundColor Green
    
    # Set up Visual Studio environment and compile Tk
    $compiletkBatch = @"
@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cd /d C:\dev\tk9.0.2\win
nmake -f makefile.vc INSTALLDIR=C:\dev\tk9.0.2\install
nmake -f makefile.vc INSTALLDIR=C:\dev\tk9.0.2\install install
echo Tk compilation complete!
pause
"@
    
    $compiletkBatch | Out-File -FilePath "compile_tk.bat" -Encoding ASCII
    Write-Host "Created compile_tk.bat to compile Tk" -ForegroundColor Yellow
    Write-Host "Run this to compile Tk, then we can build the GUI version" -ForegroundColor Yellow
    
} else {
    Write-Host "Tk source not found at C:/dev/tk9.0.2" -ForegroundColor Red
    Write-Host "Please verify the path or download Tk source" -ForegroundColor Red
}

# Also create a script to build GUI version after Tk is compiled
$guiBuildBatch = @"
@echo off
echo Building GUI version with compiled Tk...
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cd /d "%~dp0"

REM Set Tcl/Tk paths (adjust these based on your vcpkg and compiled Tk paths)
set TCL_INCLUDE=C:\dev\vcpkg\installed\x64-windows\include
set TCL_LIB=C:\dev\vcpkg\installed\x64-windows\lib
set TK_INCLUDE=C:\dev\tk9.0.2\install\include
set TK_LIB=C:\dev\tk9.0.2\install\lib

if not exist build_gui mkdir build_gui
cd build_gui

cl /EHsc /std:c++17 /I%TCL_INCLUDE% /I%TK_INCLUDE% ..\main.cpp ..\AutoStageCoordCreator.cpp ..\AutoStageGUI.cpp /link %TCL_LIB%\tcl90.lib %TK_LIB%\tk90.lib /Fe:AutoStageGUI.exe

if %ERRORLEVEL% EQU 0 (
    echo GUI build successful!
    echo Executable: build_gui\AutoStageGUI.exe
) else (
    echo GUI build failed - check Tcl/Tk paths
)
pause
"@

$guiBuildBatch | Out-File -FilePath "compile_gui.bat" -Encoding ASCII
Write-Host "Created compile_gui.bat for GUI version (run after Tk is compiled)" -ForegroundColor Yellow
