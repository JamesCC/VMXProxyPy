@echo off

echo Your IP address(es):
ipconfig | findstr /R /b /C:" *IP.*"
echo.

rem cx_freeze version
if exist start_VMXProxy.exe (
    start_VMXProxy %* || pause
    goto end
)

rem go hunting for python installation
for /d %%F in ( "C:\Python*"
                "D:\Python\Python36-32"
                "%ProgramFiles%\Python*"
                "%ProgramFiles(x86)%\Python*"
                "%LocalAppData%\Programs\Python\Python*"
                "%LocalAppData%\Programs\Python\Python*-32"
              ) do set PYTHONINSTALLDIR=%%F

if exist "%PYTHONINSTALLDIR%\python.exe" (
    echo Python found in directory %PYTHONINSTALLDIR%
    "%PYTHONINSTALLDIR%\python.exe" start_VMXProxy.py %* || pause
    goto end
) else (
    echo Unable to find python
    echo Add python install dir to for loop in %~dp0\start_VMXProxy.bat
    pause
)

:end
