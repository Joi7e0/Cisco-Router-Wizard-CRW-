@echo off
:: =========================================
:: START SCRIPT FOR PRODUCTION ENVIRONMENT
:: =========================================
echo [INFO] Starting Cisco Router Wizard in PRODUCTION mode...

:: The production script assumes PyInstaller has packaged the app into 'dist' folder
SET "PROD_EXECUTABLE=dist\CiscoRouterWizard.exe"

if exist "%PROD_EXECUTABLE%" (
    echo [INFO] Found production build. Launching...
    start "" "%PROD_EXECUTABLE%"
) else (
    echo [WARNING] Production executable not found at %PROD_EXECUTABLE%.
    echo [INFO] Attempting to build production executable first...
    
    :: Try to build if it doesn't exist
    if not exist ".venv\Scripts\Activate.bat" (
        echo [ERROR] Virtual environment is missing. Cannot build application.
        pause
        exit /b 1
    )
    
    call .venv\Scripts\Activate.bat
    echo [INFO] Building with PyInstaller...
    python -m eel backend/main.py frontend --onefile --noconsole --name "CiscoRouterWizard"
    
    if exist "%PROD_EXECUTABLE%" (
        echo [INFO] Build successful. Launching...
        start "" "%PROD_EXECUTABLE%"
    ) else (
        echo [ERROR] Build failed. Please check the logs.
        pause
        exit /b 1
    )
)
