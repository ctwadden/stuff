@echo off
echo ========================================
echo   Game AI Buddy Server - Windows
echo ========================================
echo.

cd /d "%~dp0"

:: Check if venv exists, create if not
if not exist "venv\" (
    echo Creating Python virtual environment...
    python -m venv venv
    echo Installing dependencies...
    venv\Scripts\pip install -r server\requirements.txt
)

echo Starting Game AI Buddy Server...
echo Open config.json to add your Gemini API key.
echo.
venv\Scripts\python server\main.py

pause
