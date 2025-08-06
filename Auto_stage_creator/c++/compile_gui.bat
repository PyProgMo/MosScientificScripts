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
