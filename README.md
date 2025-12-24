# Industrial Cloud Data Portfolio

A production-ready cloud data pipeline with real-time monitoring dashboard, microservices architecture, and continuous telemetry processing deployed on Google Cloud Run.

## 🌐 Live Deployment

**Dashboard Frontend:** https://dashboard-frontend-<project-id>-uc.a.run.app  
**Dashboard API:** https://dashboard-api-<project-id>-uc.a.run.app  
**API Documentation:** https://dashboard-api-<project-id>-uc.a.run.app/docs

> Replace `<project-id>` with your GCP project ID. Services are deployed automatically via GitHub Actions on push to `main` branch.

## Overview

This project demonstrates an industrial-grade telemetry system with:
- **Real-time dashboards** for monitoring infrastructure metrics
- **Continuous data pipeline** with Pub/Sub and Cloud Storage
- **FastAPI REST APIs** with automatic OpenAPI documentation
- **Microservices architecture** with independent scaling
- **PostgreSQL database** for storing processed metrics
- **Automated CI/CD** with GitHub Actions and Cloud Run

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
- **Dashboard:** http://localhost:8000
- **API:** http://localhost:8080
- **API Docs:** http://localhost:8080/docs
- Generator: http://localhost:8001/health
- Ingestion: http://localhost:8002/health
- Transformer: http://localhost:8003/health

## Automated Deployment

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
```## Automated Deployment

Every push to `main` branch triggers GitHub Actions to:
1. Build Docker images from project root
2. Push to Google Artifact Registry
3. Deploy all services to Cloud Run

**Required GitHub Secrets:**
- `GCP_PROJECT_ID` - Your GCP project ID
- `GCP_SA_KEY` - Service account JSON key
- `GCP_BUCKET_NAME` - Cloud Storage bucket name
- `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` - PostgreSQL credentials

**Monitor Deployments:** GitHub Actions tab → "Deploy to Cloud Run"
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
- Graceful integrauses:
- **Flask HTTP server** - Cloud Run compatible with PORT environment variable
- **Background daemon thread** - Continuous processing without timeout
- **Health endpoints** - `GET /health` for monitoring
- **Graceful shutdown** - Proper signal handling

**Key Benefits:**
- 24/7 continuous operation (unlike Cloud Run Jobs)
- HTTP health checks and monitoring
- Identical behavior locally and in cloud
- Independent scaling per servicer (Flask + threading)
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

# ViEnvironment Variables

Create a `.env` file with:
```bash
# GCP Configuration
GCP_PROJECT_ID=your-project-id
GCP_BUCKET_NAME=your-bucket-name

# PostgreSQL Configuration
DB_HOST=your-db-host
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-password
DB_PORT=5432
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
- Conocker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compos & Troubleshooting

### Health Checks
```bash
# Local services
curl http://localhost:8001/health  # Generator
curl http://localhost:8002/health  # Ingestion  
curl http://localhost:8003/health  # Transformer
curl http://localhost:8080/health  # Dashboard API

# Cloud Run (replace <url> with actual service URL)
curl https://<service-url>/health
```

### Common Issues

**Services not starting?**
```bash
docker-compose logs <service-name>
docker-compose restart
```

**Database connection failed?**
- Verify `.env` has correct DB credentials
- Check Cloud SQL instance is running
- Ensure authorized networks include your IP

**Build failures?**
- Clear Docker cache: `docker-compose build --no-cache`
- Check all requirements.txt files exist
- Verify Dockerfiles reference correct paths

---

**Last Updated:** December 25, 2025  
**Status:** ✅ Production - Deployed