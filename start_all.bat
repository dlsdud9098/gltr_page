@echo off
echo ===================================
echo Starting GLTR Webtoon Platform
echo ===================================
echo.

echo [1] Starting Backend Server...
start "GLTR Backend" cmd /k "cd backend && call .venv\Scripts\activate && python main.py"

echo [2] Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo [3] Starting Frontend...
start "GLTR Frontend" cmd /k "cd frontend && npm start"

echo.
echo ===================================
echo GLTR Platform is starting...
echo ===================================
echo.
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press any key to exit this window...
pause > nul