@echo off

if "%1"=="" goto noparams

echo Your IP address(es):
ipconfig | findstr /R /b /C:" *IP.*"
echo.

reg.exe Query HKLM\Hardware\Description\System\CentralProcessor\0 | find /i "x86"
if %ERRORLEVEL% == 0 (
    set DIST_PATH=dist32
) else (
    set DIST_PATH=dist64
)

if exist %DIST_PATH%\NUL (
    %DIST_PATH%\VMXProxy %*
) ELSE (
    python VMXProxy %*
)

noparams: