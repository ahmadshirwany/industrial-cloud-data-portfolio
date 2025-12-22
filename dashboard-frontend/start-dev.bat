@echo off
REM Industrial Cloud Dashboard Frontend Setup Script
REM Run this batch file after Node.js is installed

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Frontend Setup Script
echo ========================================
echo.

REM Check if Node.js is installed
echo Checking for Node.js...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Node.js is not installed or not in PATH
    echo.
    echo Please download and install Node.js from:
    echo https://nodejs.org/ ^(LTS version recommended^)
    echo.
    echo Make sure to check "Add to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Get Node version
for /f "tokens=*" %%A in ('node --version') do set NODE_VERSION=%%A
for /f "tokens=*" %%A in ('npm --version') do set NPM_VERSION=%%A

echo Found Node.js: %NODE_VERSION%
echo Found npm: %NPM_VERSION%
echo.

REM Check if npm install is needed
if not exist "node_modules" (
    echo Installing dependencies...
    echo This may take 2-5 minutes on first run...
    echo.
    call npm install
    if !ERRORLEVEL! NEQ 0 (
        echo.
        echo ERROR: npm install failed
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
    echo.
) else (
    echo Dependencies already installed.
    echo.
)

echo ========================================
echo Starting Development Server...
echo ========================================
echo.
echo Frontend will be available at:
echo   http://localhost:5173
echo.
echo Make sure the backend is running on port 8080:
echo   cd services\dashboard-api
echo   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080
echo.
echo Press Ctrl+C to stop the development server.
echo.

call npm run dev
pause
