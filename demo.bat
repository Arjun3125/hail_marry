@echo off
REM ========================================
REM  AIaaS Demo Launcher — One-Click Start
REM ========================================
REM  This script launches the demo in DEMO_MODE.
REM  No PostgreSQL, Redis, or Google OAuth needed.
REM  Uses SQLite + auto-seeded demo data.
REM ========================================

echo.
echo  ╔══════════════════════════════════════╗
echo  ║   AIaaS — Investor Demo Launcher    ║
echo  ║   No database config needed         ║
echo  ╚══════════════════════════════════════╝
echo.

REM Set demo environment variables
set DEMO_MODE=true
set APP_ENV=local
set NEXT_PUBLIC_DEMO_MODE=true
set NEXT_PUBLIC_ENABLE_DEMO_LOGIN=true
set NEXT_PUBLIC_API_URL=http://localhost:8000

echo [1/3] Starting backend (FastAPI + SQLite)...
cd /d "%~dp0backend"
start /b cmd /c "set DEMO_MODE=true && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/3] Waiting for backend...
timeout /t 3 /nobreak > nul

echo [3/3] Starting frontend (Next.js)...
cd /d "%~dp0frontend"
start /b cmd /c "set NEXT_PUBLIC_DEMO_MODE=true && set NEXT_PUBLIC_ENABLE_DEMO_LOGIN=true && set NEXT_PUBLIC_API_URL=http://localhost:8000 && npm run dev"

echo.
echo  ╔══════════════════════════════════════╗
echo  ║  Demo is starting!                  ║
echo  ║                                      ║
echo  ║  Frontend: http://localhost:3000     ║
echo  ║  Demo Page: http://localhost:3000/demo ║
echo  ║  Backend:  http://localhost:8000     ║
echo  ║  API Docs: http://localhost:8000/docs ║
echo  ║                                      ║
echo  ║  Press Ctrl+C to stop both servers   ║
echo  ╚══════════════════════════════════════╝
echo.

timeout /t 5 /nobreak > nul
start http://localhost:3000/demo
pause
