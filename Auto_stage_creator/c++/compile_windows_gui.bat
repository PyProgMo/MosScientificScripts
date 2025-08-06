@echo off
echo Building Native Windows GUI version...
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cd /d "%~dp0"

if not exist build_wingui mkdir build_wingui
cd build_wingui

cl /EHsc /std:c++17 ..\windows_gui_main.cpp ..\AutoStageCoordCreator.cpp /Fe:AutoStageGUI.exe /link user32.lib gdi32.lib comctl32.lib comdlg32.lib

if %ERRORLEVEL% EQU 0 (
    echo Windows GUI build successful!
    echo Executable: build_wingui\AutoStageGUI.exe
    echo Starting the GUI...
    AutoStageGUI.exe
) else (
    echo Windows GUI build failed
)
pause
