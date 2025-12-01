@echo off
REM Linear Task Header - Windows Launcher
REM This script launches the Linear Task Header application

echo Starting Linear Task Header...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo Dependencies not found. Installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting application...
echo Press Ctrl+C to exit
echo.

REM Run the application
python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Application exited with an error
    pause
)

