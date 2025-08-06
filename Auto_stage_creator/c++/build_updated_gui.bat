@echo off
echo Building Updated Windows GUI...
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cd /d "%~dp0\build_wingui"

cl /EHsc /std:c++17 ..\windows_gui_main.cpp ..\AutoStageCoordCreator.cpp /Fe:AutoStageGUI_Updated.exe /link user32.lib gdi32.lib comctl32.lib comdlg32.lib

if %ERRORLEVEL% EQU 0 (
    echo Updated Windows GUI build successful!
    echo Executable: build_wingui\AutoStageGUI_Updated.exe
    AutoStageGUI_Updated.exe
) else (
    echo Build failed
)
pause
