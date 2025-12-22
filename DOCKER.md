# Docker Run Guide

## Prerequisites

- Docker & Docker Compose installed
- Service account keys for each service (see config folders)
- GCP Cloud SQL PostgreSQL instance created

## Quick Start

### 1. Configure Environment

```powershell
# Copy environment template
cp .env.example .env

# Edit .env with your Cloud SQL credentials
# - DB_HOST: Your Cloud SQL IP address
# - DB_NAME: Database name (default: telemetry)
# - DB_USER: Database user
# - DB_PASSWORD: Database password
```

### 2. Place Service Account Keys

```powershell
services/generator/config/service-account.json
services/ingestion/config/service-account.json
services/transformer/config/service-account.json
```

### 3. Run All Services

```powershell
# Build and start all microservices
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Run Individual Containers

### Generator Service
```powershell
# Build
docker build -f services/generator/Dockerfile -t telemetry-generator .

# Run
docker run -d `
  --name generator `
  -e GCP_PROJECT_ID=industrial-cloud-data `
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/config/service-account.json `
  -v ${PWD}/services/generator/config:/app/config:ro `
  telemetry-generator
```

### Ingestion Service
```powershell
# Build
docker build -f services/ingestion/Dockerfile -t telemetry-ingestion .

# Run
docker run -d `
  --name ingestion `
  -e GCP_PROJECT_ID=industrial-cloud-data `
  -e GCP_BUCKET_NAME=telemetry-data007 `
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/config/service-account.json `
  -v ${PWD}/services/ingestion/config:/app/config:ro `
  telemetry-ingestion
```

### Transformer Service
```powershell
# Build
docker build -f services/transformer/Dockerfile -t telemetry-transformer .

# Run (requires database credentials)
docker run -d `
  --name transformer `
  -e GCP_PROJECT_ID=industrial-cloud-data `
  -e GCP_BUCKET_NAME=telemetry-data007 `
  -e DB_HOST=your-cloud-sql-ip `
  -e DB_NAME=telemetry `
  -e DB_USER=postgres `
  -e DB_PASSWORD=your-password `
  -e DB_PORT=5432 `
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/config/service-account.json `
  -v ${PWD}/services/transformer/config:/app/config:ro `
  telemetry-transformer
```

## Useful Commands

```powershell
# View logs
docker logs -f generator
docker logs -f ingestion
docker logs -f transformer

# View docker-compose logs
docker-compose logs -f
docker-compose logs -f transformer

# Stop services
docker stop generator ingestion transformer
docker rm generator ingestion transformer

# Restart
docker restart generator
docker restart ingestion
docker restart transformer

# Check status
docker ps

# Clean up
docker-compose down --volumes --remove-orphans
```

## Troubleshooting

### Database Connection Issues

1. **Verify Cloud SQL IP**: Check your Cloud SQL instance public IP
2. **Authorize Networks**: Add Docker host IP to Cloud SQL authorized networks
3. **Test Connection**:
   ```powershell
   docker exec -it transformer python -c "import psycopg2; conn = psycopg2.connect(host='$DB_HOST', dbname='$DB_NAME', user='$DB_USER', password='$DB_PASSWORD'); print('Connected!'); conn.close()"
   ```

### Check Logs

```powershell
# All services
docker-compose logs --tail=50

# Specific service with follow
docker-compose logs -f transformer

# Filter for errors
docker-compose logs | Select-String "ERROR"
```

### Rebuild After Changes

```powershell
# Rebuild specific service
docker-compose build transformer

# Rebuild and restart
docker-compose up -d --build transformer
```

## Production Tips

1. **Use Cloud SQL Proxy** for secure connections
2. **Store DB_PASSWORD** in Secret Manager
3. **Enable SSL** for PostgreSQL connections
4. **Use private IPs** with VPC peering
5. **Set resource limits** in docker-compose.yml
6. **Monitor with Cloud Logging**

## Requirements

- Docker Desktop installed
- Service account keys in:
  - `services/generator/config/service-account.json`
  - `services/ingestion/config/service-account.json`
  - `services/transformer/config/service-account.json`
- PostgreSQL instance (Cloud SQL) created and accessible
