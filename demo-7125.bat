@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "ROOT=%SCRIPT_DIR%"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"

echo Starting VidyaOS demo on localhost (Port 7125)...

start "VidyaOS Backend" cmd /k "cd /d "%ROOT%backend" && set DEMO_MODE=true && set APP_ENV=local && set APP_DEBUG=true && set STARTUP_CHECKS_ENABLED=false && set DATABASE_URL=sqlite:///./vidyaos_demo.db && "%PYTHON%" -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload"
start "VidyaOS Frontend (7125)" cmd /k "cd /d "%ROOT%frontend" && set NEXT_PUBLIC_DEMO_MODE=true && set NEXT_PUBLIC_ENABLE_DEMO_LOGIN=true && set NEXT_PUBLIC_API_URL=http://localhost:8080 && npm run dev -- -p 7125"

echo.
echo Frontend:  http://localhost:7125
echo Demo page: http://localhost:7125/demo
echo Backend:   http://localhost:8080
echo API docs:  http://localhost:8080/docs
echo.

timeout /t 8 /nobreak > nul
start http://localhost:7125/demo
