# Run both microservices locally in separate terminals
# Simulates true microservices deployment

$projectRoot = "D:\work\industrial-cloud-data-portfolio"

Write-Host "Starting Microservices..." -ForegroundColor Green
Write-Host ""

# Prompt for database credentials
Write-Host "Database Configuration (for Transformer Service):" -ForegroundColor Yellow
$dbHost = Read-Host "Enter DB_HOST (Cloud SQL IP)"
$dbName = Read-Host "Enter DB_NAME (default: telemetry)"
if ([string]::IsNullOrWhiteSpace($dbName)) { $dbName = "telemetry" }
$dbUser = Read-Host "Enter DB_USER"
$dbPasswordSecure = Read-Host "Enter DB_PASSWORD" -AsSecureString
$dbPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPasswordSecure))
Write-Host ""

# Start Generator Microservice
Write-Host "Starting Generator Microservice..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
    Set-Location '$projectRoot'
    `$Host.UI.RawUI.WindowTitle = 'Generator Microservice'
    Write-Host '=======================================================' -ForegroundColor Yellow
    Write-Host 'Generator Microservice Terminal' -ForegroundColor Yellow
    Write-Host '=======================================================' -ForegroundColor Yellow
    `$env:GCP_PROJECT_ID='industrial-cloud-data'
    & '$projectRoot\.venv\Scripts\python.exe' services/generator/main.py
"@

Start-Sleep -Seconds 2

# Start Ingestion Microservice
Write-Host "Starting Ingestion Microservice..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
    Set-Location '$projectRoot'
    `$Host.UI.RawUI.WindowTitle = 'Ingestion Microservice'
    Write-Host '=======================================================' -ForegroundColor Yellow
    Write-Host 'Ingestion Microservice Terminal' -ForegroundColor Yellow
    Write-Host '=======================================================' -ForegroundColor Yellow
    `$env:GCP_PROJECT_ID='industrial-cloud-data'
    `$env:GCP_BUCKET_NAME='telemetry-data007'
    & '$projectRoot\.venv\Scripts\python.exe' services/ingestion/main.py
"@

Start-Sleep -Seconds 2

# Start Transformer Microservice
Write-Host "Starting Transformer Microservice..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
    Set-Location '$projectRoot'
    `$Host.UI.RawUI.WindowTitle = 'Transformer Microservice (ETL)'
    Write-Host '=======================================================' -ForegroundColor Yellow
    Write-Host 'Transformer Microservice Terminal (ETL -> PostgreSQL)' -ForegroundColor Yellow
    Write-Host '=======================================================' -ForegroundColor Yellow
    `$env:GCP_PROJECT_ID='industrial-cloud-data'
    `$env:GCP_BUCKET_NAME='telemetry-data007'
    `$env:DB_HOST='$dbHost'
    `$env:DB_NAME='$dbName'
    `$env:DB_USER='$dbUser'
    `$env:DB_PASSWORD='$dbPassword'
    `$env:DB_PORT='5432'
    & '$projectRoot\.venv\Scripts\python.exe' services/transformer/main.py
"@

Write-Host ""
Write-Host "All microservices started in separate terminals" -ForegroundColor Green
Write-Host ""
Write-Host "Running Services:" -ForegroundColor White
Write-Host "  - Generator Microservice  -> Publishing metrics to Pub/Sub"
Write-Host "  - Ingestion Microservice  -> Consuming from Pub/Sub -> Storing to GCS"
Write-Host "  - Transformer Microservice -> ETL: GCS -> Transform -> PostgreSQL"
Write-Host ""
Write-Host "Each service runs independently with its own service account" -ForegroundColor Gray
Write-Host "Close each terminal window to stop the services" -ForegroundColor Gray
