@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cd /d C:\dev\tk9.0.2\win
nmake -f makefile.vc INSTALLDIR=C:\dev\tk9.0.2\install
nmake -f makefile.vc INSTALLDIR=C:\dev\tk9.0.2\install install
echo Tk compilation complete!
pause
