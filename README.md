# Industrial Cloud Data Portfolio

A production-ready cloud data pipeline with real-time monitoring dashboard, microservices architecture, and continuous telemetry processing.

## Overview

This project provides an industrial-grade telemetry system with:
- **Real-time dashboards** for monitoring infrastructure metrics
- **Continuous data pipeline** with Pub/Sub and Cloud Storage integration
- **FastAPI REST APIs** for accessing transformed telemetry data
- **Microservices architecture** with Flask HTTP servers and background workers
- **PostgreSQL database** for storing processed metrics
- **Docker & Cloud Run** deployment on Google Cloud Platform

## Tech Stack

**Frontend**
- Flask with Jinja2 templating
- HTMX for dynamic updates
- Tailwind CSS for styling

**Backend & APIs**
- FastAPI REST APIs
- Flask HTTP servers (Generator, Ingestion, Transformer)
- PostgreSQL 15 database
- SQLAlchemy ORM

**Data Pipeline**
- Synthetic telemetry generator (Flask + threading)
- GCP Pub/Sub for message streaming
- Google Cloud Storage for data staging
- ETL transformer service (Flask + threading)

**Cloud & Infrastructure**
- Google Cloud Platform (GCP)
- Cloud Run Services (for microservices)
- Cloud SQL (PostgreSQL database)
- Artifact Registry (Docker images)
- Docker & Docker Compose (local development)
- Python 3.11

## Quick Start

### Prerequisites
- Docker Desktop (local development)
- GCP Project with credentials (for cloud deployment)
- 4GB RAM minimum
- 10GB disk space

### Local Development

```bash
# Start all services locally
docker-compose up -d

# Wait 3 seconds, then test health endpoints
curl http://localhost:8001/health   # Generator
curl http://localhost:8002/health   # Ingestion
curl http://localhost:8003/health   # Transformer
curl http://localhost:8080/        # Dashboard API

# View logs
docker-compose logs -f generator
docker-compose logs -f ingestion
docker-compose logs -f transformer

# Stop all services
docker-compose down
```

**Access Points:**
- Frontend: http://localhost:8000
- API: http://localhost:8080
- Generator Health: http://localhost:8001/health
- Ingestion Health: http://localhost:8002/health
- Transformer Health: http://localhost:8003/health

### Cloud Deployment

Services are deployed to Google Cloud Run with automatic CI/CD:

```bash
# Generator Service
https://generator-esne4epeha-uc.a.run.app

# Ingestion Service
https://ingestion-esne4epeha-uc.a.run.app

# Transformer Service
https://transformer-esne4epeha-uc.a.run.app

# Dashboard API
https://dashboard-api-esne4epeha-uc.a.run.app

# Dashboard Frontend
https://dashboard-frontend-esne4epeha-uc.a.run.app
```

#### Automatic Deployment (CI/CD)

Every push to `main` or `develop` branch automatically deploys all services to Cloud Run.

**Setup Instructions:** See [CICD_SETUP_GUIDE.md](CICD_SETUP_GUIDE.md)

**Quick Start:**
```bash
# 1. Create GCP service account (run locally)
export PROJECT_ID="industrial-cloud-data"
gcloud iam service-accounts create github-actions-runner --display-name="GitHub Actions Runner"
# ... (see full guide for complete setup)

# 2. Add GitHub Secrets
# Settings → Secrets and variables → Actions
# - GCP_PROJECT_ID: your-project-id
# - GCP_SA_KEY: (contents of service account JSON)

# 3. Push code
git push origin main
```

**Workflow status:** GitHub Actions tab → Deploy to Cloud Run

## Architecture

### Data Flow

```
Generator Service (Pub/Sub)
    ↓
Ingestion Service (Cloud Storage)
    ↓
Transformer Service (PostgreSQL)
    ↓
Dashboard API (REST endpoints)
    ↓
Dashboard Frontend (Web UI)
```

### Services

| Service | Type | Port (Local) | Purpose |
|---------|------|-------------|---------|
| **Generator** | Cloud Run Service | 8001 | Generates synthetic telemetry data |
| **Ingestion** | Cloud Run Service | 8002 | Consumes from Pub/Sub → Cloud Storage |
| **Transformer** | Cloud Run Service | 8003 | ETL: Cloud Storage → PostgreSQL |
| **Dashboard API** | Cloud Run Service | 8080 | REST API for telemetry data |
| **Dashboard Frontend** | Cloud Run Service | 8000 | Web dashboard UI |

## Services Architecture

Each microservice (Generator, Ingestion, Transformer) uses:
- **Flask HTTP server** - Listens on PORT environment variable (Cloud Run compatible)
- **Background daemon thread** - Runs continuous work loop independently
- **Health check endpoint** - `GET /health` returns service status
- **Root endpoint** - `GET /` returns service description

This architecture enables:
- 24/7 continuous operation (unlike Cloud Run Jobs which timeout after 1 hour)
- HTTP monitoring and health checks
- Graceful integration with Cloud Run Services
- Identical behavior in local and cloud environments

## Project Structure

```
industrial-cloud-data-portfolio/
├── services/
│   ├── dashboard-api/          # FastAPI REST API server
│   ├── dashboard-frontend/     # Flask web UI
│   ├── generator/              # Telemetry generator (Flask + threading)
│   ├── ingestion/              # Pub/Sub consumer (Flask + threading)
│   └── transformer/            # ETL pipeline (Flask + threading)
├── shared/                     # Shared utilities and GCP broker
├── scripts/                    # Deployment scripts
├── docker-compose.yml          # Local development composition
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (GCP config)
└── README.md                   # This file
```

## Development

### Local Development Commands

```bash
# Build all Docker images
docker-compose build

# Build with no cache
docker-compose build --no-cache

# View real-time logs
docker-compose logs -f

# Run specific service logs
docker-compose logs -f generator

# Rebuild single service
docker-compose build generator

# Stop all containers
docker-compose stop

# Remove all containers and volumes
docker-compose down -v
```

### Environment Variables

Required in `.env` for cloud deployment:
```
DB_HOST=<PostgreSQL IP>
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=<password>
DB_PORT=5432
GCP_PROJECT_ID=industrial-cloud-data
GCP_BUCKET_NAME=telemetry-data007
```

### Database

PostgreSQL stores:
- `server_metrics` - Server CPU, memory, disk data
- `container_metrics` - Container performance data
- `service_metrics` - Service-level metrics

## Monitoring

### Health Checks (Local)
```bash
# All services respond to health checks
curl http://localhost:8001/health  # {"service":"generator","status":"healthy"...}
curl http://localhost:8002/health  # {"service":"ingestion","status":"healthy"...}
curl http://localhost:8003/health  # {"service":"transformer","status":"healthy"...}
```

### Cloud Run Services
Services are monitored via:
- Cloud Run service URLs with health endpoints
- Cloud Run logs (real-time)
- Cloud Monitoring dashboards
- Container logs in Cloud Logging

## Troubleshooting

**Services not starting locally?**
```bash
# Check Docker is running
docker ps

# View service logs
docker-compose logs generator

# Restart all services
docker-compose restart
```

**Database connection issues?**
```bash
# Check container can reach database
docker exec telemetry-transformer ping <DB_HOST>

# Verify environment variables
docker inspect telemetry-transformer | grep -A 20 "Env"
```

**Performance issues?**
```bash
# Check container resource usage
docker stats

# View detailed service logs
docker-compose logs -f <service-name>
```

## Deployment

### To Google Cloud Run

1. **Push updated Docker images:**
```bash
docker tag <service>:latest us-central1-docker.pkg.dev/<project>/<repo>/<service>:latest
docker push us-central1-docker.pkg.dev/<project>/<repo>/<service>:latest
```

2. **Deploy service:**
```bash
gcloud run deploy <service> \
  --image=us-central1-docker.pkg.dev/<project>/<repo>/<service>:latest \
  --region=us-central1 \
  --memory=512Mi \
  --set-env-vars='GCP_PROJECT_ID=<project>,GCP_BUCKET_NAME=<bucket>' \
  --allow-unauthenticated
```

## License

Portfolio project demonstrating cloud data engineering and microservices architecture.

---

**Last Updated:** December 23, 2025
**Status:** Production - All services running on Google Cloud Run
