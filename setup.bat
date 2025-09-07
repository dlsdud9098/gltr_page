@echo off
echo ===================================
echo GLTR Webtoon Platform Setup Script
echo (No Authentication Version)
echo ===================================

REM Check if PostgreSQL is installed
where psql >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] PostgreSQL is not installed or not in PATH. Please install PostgreSQL first.
    pause
    exit /b 1
)

REM Check if UV is installed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] UV is not installed. Please install UV first:
    echo    pip install uv
    pause
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

echo [OK] All required tools are installed.
echo.

REM Database setup
echo Setting up PostgreSQL database...
set /p PG_USER="Enter PostgreSQL username (default: postgres): "
if "%PG_USER%"=="" set PG_USER=postgres

set /p PG_PASSWORD="Enter PostgreSQL password: "

REM Create database
set PGPASSWORD=%PG_PASSWORD%
psql -U %PG_USER% -c "CREATE DATABASE gltr_webtoon;" 2>nul
if %errorlevel% equ 0 (
    echo [OK] Database created successfully.
) else (
    echo [WARNING] Database might already exist or creation failed.
)

REM Apply schema
if exist database\schema.sql (
    psql -U %PG_USER% -d gltr_webtoon -f database\schema.sql
    echo [OK] Database schema applied.
) else (
    echo [ERROR] Schema file not found at database\schema.sql
)

REM Backend setup
echo.
echo Setting up Backend...
cd backend

REM Create virtual environment
call uv venv
echo [OK] Virtual environment created.

REM Install dependencies
call .venv\Scripts\activate
call uv pip install -r requirements.txt
echo [OK] Backend dependencies installed.

REM Create .env file
if not exist .env (
    (
        echo DATABASE_URL=postgresql://%PG_USER%:%PG_PASSWORD%@localhost:5432/gltr_webtoon
        echo HOST=0.0.0.0
        echo PORT=8000
        echo CORS_ORIGINS=http://localhost:3000,http://localhost:3001
    ) > .env
    echo [OK] Backend .env file created.
) else (
    echo [WARNING] Backend .env file already exists.
)

cd ..

REM Frontend setup
echo.
echo Setting up Frontend...
cd frontend

REM Install dependencies
call npm install
echo [OK] Frontend dependencies installed.

cd ..

REM Clean up old auth-related files
echo.
echo Cleaning up old authentication files...
del backend\auth.py 2>nul
del backend\routers\auth_router.py 2>nul
del backend\routers\users_router.py 2>nul
del frontend\src\contexts\AuthContext.js 2>nul
del frontend\src\components\PrivateRoute.js 2>nul
del frontend\src\pages\LoginPage.js 2>nul
del frontend\src\pages\LoginPage.css 2>nul
del frontend\src\pages\RegisterPage.js 2>nul
del frontend\src\pages\RegisterPage.css 2>nul
del frontend\src\pages\ProfilePage.js 2>nul
del frontend\src\pages\ProfilePage.css 2>nul
echo [OK] Old authentication files removed.

echo.
echo ===================================
echo [OK] Setup completed successfully!
echo ===================================
echo.
echo This version works without login/signup!
echo Sessions are managed automatically via browser cookies.
echo.
echo To start the application:
echo.
echo 1. Start Backend:
echo    cd backend
echo    .venv\Scripts\activate
echo    python main.py
echo.
echo 2. Start Frontend (in a new terminal):
echo    cd frontend
echo    npm start
echo.
echo The application will be available at:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo Features:
echo    - No login required
echo    - Session-based ownership (30 days)
echo    - Create and manage webtoons anonymously
echo    - All data tied to browser session
echo.
pause