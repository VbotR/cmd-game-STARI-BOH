@echo off

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b
)

:: Install necessary libraries
echo Installing necessary libraries...
pip install pygame >nul 2>&1
if %errorlevel% neq 0 (
    echo Failed to install pygame. Please check your internet connection or pip installation.
    pause
    exit /b
)

:: Run the game
echo Starting the game...
python game.py

pause
