@echo off
echo Setting up Python environment for SOQL Query Generator...

REM Check if Python 3.8+ is installed
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8+ and try again.
    exit /b 1
)

for /f "tokens=2" %%I in ('python --version 2^>^&1') do set python_version=%%I
for /f "tokens=1,2 delims=." %%a in ("%python_version%") do (
    set python_major=%%a
    set python_minor=%%b
)

if %python_major% LSS 3 (
    echo Error: Python 3.8 or higher is required.
    echo Current version: %python_version%
    echo Please install Python 3.8+ and try again.
    exit /b 1
)

if %python_major% EQU 3 (
    if %python_minor% LSS 8 (
        echo Error: Python 3.8 or higher is required.
        echo Current version: %python_version%
        echo Please install Python 3.8+ and try again.
        exit /b 1
    )
)

echo Python %python_version% detected.

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to create virtual environment.
        echo Please make sure you have the venv module installed.
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete! The Python environment is now ready.
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To run the example script, run:
echo   python example.py
echo.
echo To run the main application, run:
echo   python main.py
echo.

pause