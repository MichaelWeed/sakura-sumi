@echo off
REM Double-click to install (if needed) and launch the Sakura Sumi web portal.
REM Windows: place this file in the project root and double-click.

setlocal
cd /d "%~dp0"

where python >nul 2>nul || where py >nul 2>nul
if errorlevel 1 (
    echo Python not found. Install from https://www.python.org/downloads/
    pause
    exit /b 1
)
if exist "venv\Scripts\python.exe" goto :run
py -m venv venv 2>nul || python -m venv venv
if errorlevel 1 (
    echo Failed to create venv. Is Python installed?
    pause
    exit /b 1
)
:run
call venv\Scripts\activate.bat

python -c "import flask" 2>nul
if errorlevel 1 (
    pip install -q -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies.
        pause
        exit /b 1
    )
)

REM Start browser after a short delay
start /b cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5001"

echo Sakura Sumi running at http://localhost:5001 — Ctrl+C to quit.
venv\Scripts\python.exe scripts\run_web.py >> sakura-sumi-web.log 2>&1
if errorlevel 1 (
    type sakura-sumi-web.log
    pause
)
endlocal
