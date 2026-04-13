@echo off
REM Start backend API server for E2E testing
cd /d "%~dp0backend"
echo [Backend] Starting API server on port 8000...
python run_api.py --host 127.0.0.1 --port 8000
pause
