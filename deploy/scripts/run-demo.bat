@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "ROOT=%%~fI\"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
  echo Missing virtual environment Python at "%PYTHON%"
  echo Create the venv first, then rerun this launcher.
  exit /b 1
)

echo Starting VidyaOS demo on localhost...

start "VidyaOS Backend" cmd /k "cd /d "%ROOT%backend" && set DEMO_MODE=true && set APP_ENV=local && set DATABASE_URL=sqlite:///./vidyaos_demo.db && "%PYTHON%" -m uvicorn main:app --host 0.0.0.0 --port 7125 --reload"
start "VidyaOS Frontend" cmd /k "cd /d "%ROOT%frontend" && set NEXT_PUBLIC_DEMO_MODE=true && set NEXT_PUBLIC_ENABLE_DEMO_LOGIN=true && set NEXT_PUBLIC_API_URL=http://localhost:7125 && npm run dev"

echo.
echo Frontend:  http://localhost:3000
echo Demo page: http://localhost:3000/demo
echo Backend:   http://localhost:7125
echo API docs:  http://localhost:7125/docs
echo.

timeout /t 5 /nobreak > nul
start http://localhost:3000/demo
