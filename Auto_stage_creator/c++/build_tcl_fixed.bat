@echo off
echo Building Tcl/Tk GUI with Fixed Stepsize Calculation...
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"

rem You need to have Tcl/Tk installed (e.g., ActiveTcl) and adjust paths as needed
rem This is a template - adjust the include and library paths for your Tcl/Tk installation

cl /EHsc /std:c++17 /I"C:\Tcl\include" main_tcl.cpp AutoStageGUI.cpp AutoStageCoordCreator.cpp /link /LIBPATH:"C:\Tcl\lib" tcl86.lib tk86.lib user32.lib gdi32.lib /out:AutoStageGUI_Tcl_Fixed.exe

if %ERRORLEVEL% == 0 (
    echo Build successful! Executable: AutoStageGUI_Tcl_Fixed.exe
    echo Note: Requires Tcl/Tk runtime libraries to run
) else (
    echo Build failed - Make sure Tcl/Tk is installed and paths are correct
)
pause
