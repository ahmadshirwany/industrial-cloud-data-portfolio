@echo off
REM Industrial Cloud Data Dashboard - Quick Start Script for Windows

echo.
echo ========================================
echo Industrial Cloud Data Dashboard
echo Quick Start Setup
echo ========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo.
    echo Please create a .env file in the project root with the following content:
    echo.
    echo DB_HOST=localhost
    echo DB_NAME=telemetry
    echo DB_USER=postgres
    echo DB_PASSWORD=your_password
    echo DB_PORT=5432
    echo GCP_PROJECT_ID=your-project-id
    echo GCP_BUCKET_NAME=telemetry-bucket
    echo.
    pause
    exit /b 1
)

echo [1/4] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not in PATH!
    pause
    exit /b 1
)
echo Docker found: OK

echo.
echo [2/4] Stopping existing containers...
docker-compose down >nul 2>&1
if errorlevel 0 (
    echo Existing containers stopped: OK
)

echo.
echo [3/4] Building and starting services...
docker-compose up --build -d
if errorlevel 1 (
    echo ERROR: Failed to start services!
    docker-compose logs
    pause
    exit /b 1
)
echo Services started: OK

echo.
echo [4/4] Waiting for services to be ready...
echo.
timeout /t 10 /nobreak

echo.
echo ========================================
echo Dashboard is Ready!
echo ========================================
echo.
echo Services running:
echo   Dashboard Frontend: http://localhost:8000
echo   Dashboard API:      http://localhost:8080
echo   API Documentation:  http://localhost:8080/docs
echo.
echo View logs with:
echo   docker-compose logs -f [service-name]
echo.
echo Available services:
echo   - generator
echo   - ingestion
echo   - transformer
echo   - dashboard-api
echo   - dashboard-frontend
echo.
echo Stop all services with:
echo   docker-compose down
echo.
pause
