@echo off
set DIST_PATH=dist

if "%1"=="" goto end

echo Your IP address(es):
ipconfig | findstr /R /b /C:" *IP.*"
echo.

rem py2exe version
if exist %DIST_PATH%\NUL (
    %DIST_PATH%\VMXProxy %*
    goto end
)

rem go hunting for python installation
for /d %%F in ( "C:\Pydthon*" "%ProgramFiles%\Python *"
                "%ProgramFiles(x86)%\Python *"
                "%LocalAppData%\Programs\Python*" 
                "%LocalAppData%\Programs\Python*-32") do set PYTHONINSTALLDIR=%%F

if exist %PYTHONINSTALLDIR%\python.exe (
    %PYTHONINSTALLDIR%\python VMXProxy %*
    goto end
) else (
    echo Unable to find python
    echo Add python install dir to for loop in %~dp0\start_VMXProxy.bat
)

:end
pause