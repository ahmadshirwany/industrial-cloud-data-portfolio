# Industrial Cloud Data Portfolio Dashboard

A comprehensive real-time monitoring dashboard for cloud infrastructure with telemetry data visualization, server/container metrics, and professional profile integration.

## Overview

This project provides a full-stack monitoring solution with:
- **Real-time dashboards** for servers, containers, and services
- **Data pipeline** for ingesting and transforming telemetry metrics
- **REST APIs** for accessing infrastructure data
- **Professional profile page** showcasing CV and portfolio
- **Docker-based microservices** architecture

## Tech Stack

**Frontend**
- FastAPI + Jinja2 templating
- HTMX for dynamic table updates
- Tailwind CSS for styling

**Backend**
- FastAPI REST APIs
- PostgreSQL database
- SQLAlchemy ORM

**Data Pipeline**
- Python telemetry generator
- GCP Pub/Sub messaging
- Google Cloud Storage (GCS)
- Data transformer service

**Infrastructure**
- Docker & Docker Compose
- PostgreSQL 15
- Python 3.11

## Quick Start

### Prerequisites
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- 4GB RAM minimum
- 10GB disk space

### Setup & Installation

See [SETUP.md](SETUP.md) for detailed initial setup instructions.

**Quick commands:**
```powershell
cd D:\work\industrial-cloud-data-portfolio
docker-compose up -d
```

Wait 30 seconds for services to initialize, then:
- Frontend: http://localhost:8000
- API Docs: http://localhost:8080/docs
- Dashboard: http://localhost:8000/dashboard

### Rebuild & Restart

See [REBUILD_GUIDE.md](REBUILD_GUIDE.md) for complete rebuild instructions.

## Features

### Dashboard Sections

**Home** - Navigation to all sections with status cards

**Servers** - Real-time server metrics
- CPU, memory, disk utilization
- Server status and uptime
- Auto-refreshing every 30 seconds

**Containers** - Docker container monitoring
- Container IDs and service names
- CPU/memory usage with progress bars
- Health status badges

**Profile** - Professional CV/Portfolio page
- Professional summary
- Skills showcase
- Work experience
- Portfolio projects
- Education and certifications

## Services

| Service | Port | Purpose |
|---------|------|---------|
| **dashboard-frontend** | 8000 | Web UI and static content |
| **dashboard-api** | 8080 | REST APIs and database |
| **generator** | — | Generates telemetry data |
| **ingestion** | — | Ingests data to GCS |
| **transformer** | — | Transforms & loads to DB |

## Project Structure

```
industrial-cloud-data-portfolio/
├── services/
│   ├── dashboard-frontend/
│   ├── dashboard-api/
│   ├── generator/
│   ├── ingestion/
│   └── transformer/
├── shared/
├── docker-compose.yml
├── REBUILD_GUIDE.md
├── SETUP.md
└── README.md
```

## Documentation

- **[README.md](README.md)** - This file (project overview)
- **[SETUP.md](SETUP.md)** - Initial setup and installation
- **[REBUILD_GUIDE.md](REBUILD_GUIDE.md)** - Docker rebuild instructions

## Development

### Making Changes

1. **Frontend** - Modify templates in `services/dashboard-frontend/templates/`
2. **Backend** - Edit routes in `services/dashboard-api/routers/`
3. **Generator** - Update `services/generator/generator_service.py`

After changes, rebuild affected service (see REBUILD_GUIDE.md).

### Database

PostgreSQL persists data in Docker volumes. Data survives rebuilds unless explicitly deleted.

## Troubleshooting

**Services not starting?**
- Check Docker Desktop is running
- Verify ports 8000 and 8080 are not in use
- Check logs: `docker-compose logs`

**Database connection error?**
- Wait 30 seconds after startup
- Restart all services: `docker-compose restart`

**Performance issues?**
- Check resource usage: `docker stats`
- Rebuild with fresh cache: See REBUILD_GUIDE.md

## License

Portfolio project demonstrating cloud monitoring and full-stack development.

---

**Last Updated**: December 22, 2025
