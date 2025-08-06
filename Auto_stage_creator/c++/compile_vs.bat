@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
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
