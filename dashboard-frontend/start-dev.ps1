# Industrial Cloud Dashboard Frontend Setup Script
# Run this PowerShell script after Node.js is installed

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Frontend Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
Write-Host "Checking for Node.js..." -ForegroundColor Yellow
$nodeCheck = Get-Command node -ErrorAction SilentlyContinue
$npmCheck = Get-Command npm -ErrorAction SilentlyContinue

if (-not $nodeCheck -or -not $npmCheck) {
    Write-Host ""
    Write-Host "ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download and install Node.js from:" -ForegroundColor Yellow
    Write-Host "https://nodejs.org/ (LTS version recommended)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Make sure to check 'Add to PATH' during installation." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Get versions
$nodeVersion = node --version
$npmVersion = npm --version

Write-Host "Found Node.js: $nodeVersion" -ForegroundColor Green
Write-Host "Found npm: $npmVersion" -ForegroundColor Green
Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    Write-Host "This may take 2-5 minutes on first run..." -ForegroundColor Yellow
    Write-Host ""
    
    npm install
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: npm install failed" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host ""
    Write-Host "Dependencies installed successfully!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Dependencies already installed." -ForegroundColor Green
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Development Server..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend will be available at:" -ForegroundColor Yellow
Write-Host "  http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Make sure the backend is running on port 8080:" -ForegroundColor Yellow
Write-Host "  cd services\dashboard-api" -ForegroundColor Gray
Write-Host "  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the development server." -ForegroundColor Yellow
Write-Host ""

npm run dev
