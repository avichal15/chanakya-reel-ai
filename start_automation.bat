@echo off
:: ═══════════════════════════════════════════════════════
:: Chanakya Reel AI - Automation Launcher
:: Uses ABSOLUTE paths to avoid PATH issues on boot
:: ═══════════════════════════════════════════════════════

:: Absolute paths
set "PROJECT_DIR=c:\Users\avich\Downloads\chanakya-reel-ai"
set "PYTHON_EXE=c:\Users\avich\Downloads\chanakya-reel-ai\.venv\Scripts\python.exe"
set "NPM_CMD=C:\Program Files\nodejs\npm.cmd"

:: Navigate to project directory
cd /d "%PROJECT_DIR%"

:: Log startup
echo [%date% %time%] Starting Chanakya AI Automation... >> "%PROJECT_DIR%\backend\startup.log"

:: Start Uvicorn Backend
echo [%date% %time%] Starting Backend... >> "%PROJECT_DIR%\backend\startup.log"
start "" /min cmd /c "cd /d "%PROJECT_DIR%" && "%PYTHON_EXE%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --log-level info"

:: Start Vite Frontend
echo [%date% %time%] Starting Frontend... >> "%PROJECT_DIR%\backend\startup.log"
start "" /min cmd /c "cd /d "%PROJECT_DIR%" && "%NPM_CMD%" run dev"

:: Wait for backend to initialize
echo [%date% %time%] Waiting 20s for services... >> "%PROJECT_DIR%\backend\startup.log"
timeout /t 20 /nobreak > nul

:: Start Scheduler
echo [%date% %time%] Starting Scheduler... >> "%PROJECT_DIR%\backend\startup.log"
start "" /min cmd /c "cd /d "%PROJECT_DIR%" && "%PYTHON_EXE%" backend/scheduler.py"

echo [%date% %time%] All services launched. >> "%PROJECT_DIR%\backend\startup.log"

:: Exit cleanly
exit
