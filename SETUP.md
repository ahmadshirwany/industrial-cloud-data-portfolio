# Setup Guide - Industrial Cloud Data Portfolio Dashboard

Complete instructions for setting up and running the project.

## Prerequisites
**System Requirements**
- Docker Desktop 4.0+ (Windows/Mac) or Docker Engine 20.10+ (Linux)
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space
- Windows 10/11 Pro, Mac OS 10.15+, or Linux with systemd

**Software**
- PowerShell 5.1+ (Windows)
- Git (optional, for version control)

## Installation Steps

### Step 1: Get the Project

Clone or download the project:

```powershell
cd D:\work
git clone <repository-url>
cd industrial-cloud-data-portfolio
```

Or if already downloaded, navigate to the project:
```powershell
cd D:\work\industrial-cloud-data-portfolio
```

### Step 2: Verify Docker Installation

Ensure Docker Desktop is running:

```powershell
docker --version
docker-compose --version
```

Expected output:
```
Docker version 20.10.x or higher
Docker Compose version v2.x or higher
```

### Step 3: Start Services

First time startup:

```powershell
cd D:\work\industrial-cloud-data-portfolio

# Start all services in background
docker-compose up -d

# Wait 30 seconds for services to initialize
Start-Sleep 30

# Verify all services are running
docker-compose ps
```

Expected output - all 5 containers should show "Up":
```
NAME                    SERVICE             STATUS
dashboard-frontend      dashboard-frontend  Up
dashboard-api           dashboard-api       Up
telemetry-generator     generator           Up
telemetry-ingestion     ingestion           Up
telemetry-transformer   transformer         Up
```

### Step 4: Access the Dashboard

Open your browser and navigate to:

- **Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8080/docs
- **API Base URL**: http://localhost:8080/api

You should see:
- Dashboard with navigation cards
- Servers tab with live server metrics
- Containers tab with container data
- Profile page with CV/portfolio
- API documentation (Swagger UI)

### Step 5: Verify Data Flow

Check that data is being generated and processed:

```powershell
# Check generator logs
docker logs generator --tail 10

# Expected output: "Publishing metrics every 5 minutes (conserving database space)"
```

Test the API:
```powershell
# Get server data
Invoke-RestMethod -Uri "http://localhost:8080/api/servers/current?limit=5"

# Expected: JSON array with server metrics
```

## Configuration

### Environment Variables

Create `.env` file in project root (optional):

```env
# Database
DB_HOST=postgres
DB_NAME=telemetry
DB_USER=postgres
DB_PASSWORD=postgres

# API
API_BASE_URL=http://dashboard-api:8080

# GCP (optional, for cloud deployment)
GCP_PROJECT_ID=your-project-id
GCP_BUCKET_NAME=your-bucket-name
```

### Service Account Keys

For GCP services (if using cloud features):

1. Create service account keys in Google Cloud Console
2. Place keys in:
   - `services/generator/config/service-account.json`
   - `services/ingestion/config/service-account.json`
   - `services/transformer/config/service-account.json`

## Verify Installation

Run these commands to confirm everything works:

```powershell
# 1. Check services are running
docker-compose ps

# 2. Test API connectivity
Invoke-RestMethod -Uri "http://localhost:8080/api/servers/current?limit=1"

# 3. Check dashboard frontend loads
Invoke-WebRequest -Uri "http://localhost:8000/" | Select-Object -ExpandProperty StatusCode
# Should return: 200

# 4. Verify no errors in logs
docker-compose logs --tail 20 | findstr ERROR
# Should return nothing (no errors)
```

## Common Issues

### Issue: "Docker daemon not running"

**Solution**: Start Docker Desktop
- Windows/Mac: Click Docker Desktop icon
- Linux: `sudo systemctl start docker`
- Wait 30 seconds for it to fully start

### Issue: "Port 8000 or 8080 already in use"

**Solution**: Stop conflicting services
```powershell
# Stop all project services
docker-compose down

# List what's using the ports (Windows)
netstat -ano | findstr :8000
netstat -ano | findstr :8080

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Restart project
docker-compose up -d
```

### Issue: Services restart repeatedly

**Solution**: Check logs for errors
```powershell
docker logs dashboard-api --tail 50
docker logs dashboard-frontend --tail 50
```

Common causes:
- Database not ready - wait 30 seconds
- Missing environment variables - check `.env` file
- Insufficient resources - close other apps

### Issue: "Cannot connect to database"

**Solution**: Restart all services
```powershell
docker-compose restart
Start-Sleep 30
docker-compose ps
```

## Next Steps

### Explore the Dashboard
1. Navigate to http://localhost:8000
2. View the Servers tab - live server metrics
3. Check Containers tab - container monitoring
4. Visit Profile page - professional CV
5. Check API docs at http://localhost:8080/docs

### Make Changes

See REBUILD_GUIDE.md for:
- Modifying code and templates
- Rebuilding services
- Troubleshooting issues

### Monitor Data Generation

Check what the generator is producing:
```powershell
# Watch generator logs in real-time
docker logs -f generator

# You'll see metrics being published every 5 minutes
```

## Stopping Services

To stop all services (data persists):
```powershell
docker-compose down
```

To start again:
```powershell
docker-compose up -d
```

To stop and delete all data:
```powershell
docker-compose down -v
```

Warning: `-v` flag deletes database data!

## Getting Help

**Check logs first**:
```powershell
# All services
docker-compose logs --tail 50

# Specific service
docker logs <service-name> --tail 20

# Follow logs (live)
docker logs -f <service-name>
```

**Check status**:
```powershell
docker-compose ps
docker stats
```

**Restart everything**:
```powershell
docker-compose restart
Start-Sleep 30
docker-compose ps
```

## References

- [README.md](README.md) - Project overview
- [REBUILD_GUIDE.md](REBUILD_GUIDE.md) - Docker rebuild & modification guide
- Docker documentation: https://docs.docker.com

---

**Last Updated**: December 22, 2025
