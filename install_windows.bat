
@echo off
echo Installing ISBN Manager...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found! Please install Python 3.11 or later.
    pause
    exit /b 1
)

REM Install required packages
echo Installing required packages...
pip install -r requirements.txt

REM Create database
echo Setting up database...
python -c "from app import db; db.create_all()"

echo Installation complete!
echo Starting application...
python run_local.py
pause
