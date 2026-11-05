@echo off
cd /d "%~dp0"
echo ===================================================================
echo     Launching IBPS RRB PO 20 Full Mock Tests Portal
echo ===================================================================
echo.
echo Starting web server and opening browser at http://localhost:8000 ...
start "" http://localhost:8000

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python -m http.server 8000
    goto :eof
)

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    py -m http.server 8000
    goto :eof
)

echo.
echo [NOTE] Python is not installed or not in PATH.
echo However, you can open index.html directly in any browser!
echo.
pause

