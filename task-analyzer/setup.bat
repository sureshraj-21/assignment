@echo off
REM Task Analyzer - Startup Script for Windows

echo.
echo ========================================
echo Task Analyzer - Startup Script
echo ========================================
echo.

REM Check if .venv exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

echo.
echo Installing/updating dependencies...
pip install -r requirements.txt -q

echo.
echo Running migrations...
python manage.py migrate -q

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the application:
echo.
echo 1. Start the Django backend (keep running):
echo    python manage.py runserver 127.0.0.1:8000 --noreload
echo.
echo 2. Open the frontend in your browser:
echo    index.html
echo.
echo Or visit: file:///C:/Users/sureshraj/task-analyzer/index.html
echo.
echo ========================================
echo.

pause
