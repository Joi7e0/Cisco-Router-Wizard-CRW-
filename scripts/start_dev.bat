@echo off
:: =========================================
:: START SCRIPT FOR DEVELOPMENT ENVIRONMENT
:: =========================================
echo [INFO] Starting Cisco Router Wizard in DEVELOPMENT mode...

:: Check if virtual environment exists
if not exist ".venv\Scripts\Activate.bat" (
    echo [ERROR] Virtual environment not found. Please run 'py -m venv .venv' and install requirements first.
    pause
    exit /b 1
)

:: Activate virtual environment
call .venv\Scripts\Activate.bat
echo [INFO] Virtual environment activated.

:: Run the application from source
echo [INFO] Launching backend.main...
py -m backend.main

echo [INFO] Development server stopped.
pause
