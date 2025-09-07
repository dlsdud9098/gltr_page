@echo off
echo Starting GLTR Backend Server...
cd backend
call .venv\Scripts\activate
echo Backend server is starting on http://localhost:8000
python main.py
pause