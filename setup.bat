@echo off
REM AutoCraftCV Setup Script for Windows
REM This script automates the setup process for Windows users

echo ============================================
echo   AutoCraftCV Setup Script for Windows
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python is installed
echo.

REM Check if we're in the right directory
if not exist "manage.py" (
    echo ❌ Error: manage.py not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo ✅ Found manage.py - in correct directory
echo.

REM Run the Python setup script
echo 🚀 Running Python setup script...
python setup.py

if %errorlevel% neq 0 (
    echo ❌ Setup failed. Please check the errors above.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Setup Complete! 🎉
echo ============================================
echo.
echo Next steps:
echo   1. Activate virtual environment: venv\Scripts\activate
echo   2. Start development server: python manage.py runserver
echo   3. Open browser to: http://127.0.0.1:8000
echo.
echo For API configuration (paid version):
echo   - Edit .env file with your API keys
echo   - Set APP_VERSION=paid in .env
echo.
echo For help, see README.md
echo.
pause
