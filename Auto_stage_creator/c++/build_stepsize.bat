@echo off
echo Building Windows GUI with Stepsize Display...
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cl /EHsc /std:c++17 windows_gui_main.cpp AutoStageCoordCreator.cpp /link user32.lib gdi32.lib comctl32.lib comdlg32.lib /out:AutoStageGUI_WithStepsize.exe
if %ERRORLEVEL% == 0 (
    echo Build successful! Executable: AutoStageGUI_WithStepsize.exe
) else (
    echo Build failed
)
pause
