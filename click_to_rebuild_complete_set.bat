@echo off
REM Windows Retail Analytics System - Complete Rebuild
REM Double-click to run this script on Windows

cls
echo ⚡ Windows Retail Analytics System - Complete Rebuild
echo =================================================

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo 📁 Working directory: %SCRIPT_DIR%

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check for virtual environment
if not exist ".venv" (
    echo 🔧 Creating Python virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo 🚀 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install required packages
echo 📥 Installing required packages...
pip install pandas numpy matplotlib seaborn duckdb fastapi uvicorn tqdm

if %errorlevel% neq 0 (
    echo ❌ Failed to install packages
    pause
    exit /b 1
)

echo ✅ All packages installed successfully

REM Remove existing database if it exists
if exist "sales_timeseries.db" (
    echo 🗑️  Removing existing database...
    del sales_timeseries.db
    echo ✅ Database removed
)

REM Generate new database
echo ⚡ Generating new comprehensive retail database...
python main.py

if %errorlevel% neq 0 (
    echo ❌ Failed to generate database
    pause
    exit /b 1
)

echo.
echo 🎉 SYSTEM REBUILD COMPLETE!
echo ==============================
echo 📊 Database: sales_timeseries.db
echo 🔧 Virtual environment: .venv\
echo 📁 All files ready in: %SCRIPT_DIR%
echo.
echo 🚀 Available tools:
echo    • python main.py --menu        (Launch retail menu)
echo    • python pack_csv.py           (CSV pack/unpack tool)
echo    • python app.py                (Start FastAPI server)
echo    • python retail_menu.py        (Direct menu access)
echo.

REM Ask if user wants to launch the menu
set /p launch_menu=🚀 Launch retail menu now? (y/n): 
if /i "%launch_menu%"=="y" (
    echo 🚀 Starting retail menu...
    python main.py --menu
)

echo 👋 Script completed. You can close this window.
pause
