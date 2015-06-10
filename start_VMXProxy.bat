@echo off
set DIST_PATH=dist

if "%1"=="" goto noparams

echo Your IP address(es):
ipconfig | findstr /R /b /C:" *IP.*"
echo.

if exist %DIST_PATH%\NUL (
    %DIST_PATH%\VMXProxy %*
) ELSE (
    python VMXProxy %*
)

:noparams
pause