# Industrial Cloud Data Dashboard - Complete Setup Guide

## Project Overview

This is a full-stack telemetry dashboard application with real-time data visualization for industrial cloud infrastructure monitoring.

**Architecture:**
```
Generator → Pub/Sub → Ingestion → Cloud Storage → Transformer → PostgreSQL → Dashboard API (FastAPI) → Dashboard Frontend (React)
```

## Services

### 1. **Telemetry Generator** (`services/generator/`)
- Generates synthetic industrial telemetry data
- Publishes to Google Cloud Pub/Sub every 30 seconds

### 2. **Ingestion Service** (`services/ingestion/`)
- Subscribes to Pub/Sub messages
- Stores raw data to Google Cloud Storage (JSONL format)

### 3. **Transformer Service** (`services/transformer/`)
- Reads from Cloud Storage every 60 seconds
- Transforms and aggregates data
- Writes to PostgreSQL database

### 4. **Dashboard API** (`services/dashboard-api/`)
- FastAPI backend (port 8080)
- 30+ REST endpoints for data retrieval
- WebSocket support for real-time updates
- All data fetching from PostgreSQL

### 5. **Dashboard Frontend** (`dashboard-frontend/`)
- React 18 + TypeScript + Vite
- Recharts for data visualizations
- 5 dashboard views: Overview, Servers, Services, Containers, Analytics
- Tailwind CSS for styling
- Real-time WebSocket connections

## Database Schema

### PostgreSQL Tables

**server_metrics** (14 columns)
- server_id, timestamp, cpu_percent, memory_percent, disk_percent, status, region, environment, request_count, error_count, success_rate, response_time_ms, disk_used_gb, disk_total_gb

**container_metrics** (16 columns)
- container_id, timestamp, service_name, cpu_percent, memory_utilization, memory_mb, memory_limit_mb, requests_per_sec, health, restart_count, uptime_seconds, network_in_bytes, network_out_bytes, disk_read_mb, disk_write_mb, region

**service_metrics** (16 columns)
- service_name, timestamp, response_time_ms, error_rate, success_rate, requests_per_second, latency_p50, latency_p95, latency_p99, throughput_mbps, cpu_utilization, memory_utilization, instance_count, active_instances, region, status

## API Endpoints (30+)

### Server Endpoints
- `GET /api/servers/health` - Server health summary
- `GET /api/servers/current` - Current server metrics
- `GET /api/servers/trends/cpu` - CPU trends
- `GET /api/servers/by-region` - Servers grouped by region
- `GET /api/servers/top-cpu` - Top CPU consumers
- `GET /api/servers/disk-usage` - Disk usage metrics

### Container Endpoints
- `GET /api/containers/health` - Container health
- `GET /api/containers/current` - Current containers
- `GET /api/containers/by-service` - Containers by service
- `GET /api/containers/high-memory` - High memory containers
- `GET /api/containers/restarts` - Restart statistics
- `GET /api/containers/throughput-trend` - Throughput trends

### Service Endpoints
- `GET /api/services/performance` - Service performance metrics
- `GET /api/services/latency-trend` - Latency trends
- `GET /api/services/error-rate-trend` - Error rate trends
- `GET /api/services/success-rate` - Success rate gauges
- `GET /api/services/failed-requests` - Failed requests
- `GET /api/services/instances` - Service instances
- `GET /api/services/by-region` - Services by region
- `GET /api/services/slowest` - Slowest services

### Analytics Endpoints
- `GET /api/analytics/system-health` - Overall system health
- `GET /api/analytics/top-cpu-resources` - Top CPU consumers
- `GET /api/analytics/top-memory-resources` - Top memory consumers
- `GET /api/analytics/anomalies` - Anomaly detection
- `GET /api/analytics/daily-stats` - Daily statistics
- `GET /api/analytics/capacity-forecast` - Capacity forecasting
- `GET /api/analytics/regional-summary` - Regional summary

### WebSocket
- `WS /api/ws/metrics` - Real-time metric streaming (30s intervals)

## Setup Instructions

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend)
- PostgreSQL 14+
- GCP service account key

### Environment Variables (.env)
```env
DB_HOST=localhost
DB_NAME=telemetry
DB_USER=postgres
DB_PASSWORD=your_secure_password_here
DB_PORT=5432
GCP_PROJECT_ID=your-project-id
GCP_BUCKET_NAME=telemetry-data007
```

### Docker Compose Deployment

```bash
# Navigate to project root
cd /path/to/industrial-cloud-data-portfolio

# Start all services
docker-compose up --build

# Services will be available at:
# - Dashboard API: http://localhost:8080
# - Dashboard Frontend: http://localhost:5173
# - API Docs: http://localhost:8080/docs
```

### Running Individual Services

```bash
# Start specific service
docker-compose up --build dashboard-frontend

# View logs
docker-compose logs -f dashboard-frontend

# Stop all services
docker-compose down

# Remove all containers and volumes
docker-compose down -v
```

### Local Development

#### Backend (FastAPI)
```bash
cd services/dashboard-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn main:app --reload --port 8080
```

#### Frontend (React)
```bash
cd dashboard-frontend

# Install dependencies
npm install

# Development server (with API proxy)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Testing

### API Testing
```bash
# Run comprehensive API test script
cd /path/to/project
python test_dashboard_api.py

# Expected output: 30/30 tests passing (100% success rate)
```

### Frontend Testing
```bash
cd dashboard-frontend

# Run unit tests
npm run test

# Run with coverage
npm run test:coverage
```

## Dashboard Features

### Overview Dashboard
- System health score (0-100)
- CPU, Memory, Disk utilization (last 5 min)
- Resource trends chart (stacked area)
- Health score gauge (donut chart)
- 24-hour statistics

### Servers Dashboard
- Server health summary (healthy/warning/critical count)
- CPU trends (24 hours)
- Servers by region (bar chart)
- Top CPU consumers (table)
- High disk usage alerts (>50%)

### Services Dashboard
- Service performance cards (success rate, latency, error rate)
- Latency trend (24 hours)
- Error rate trend (24 hours)
- Success rate gauge (current 5 min)
- Slowest services (table)
- Failed requests analysis

### Containers Dashboard
- Container health summary
- Request throughput trend (24 hours)
- Containers by service (bar chart)
- Current containers table
- High memory containers alert (>80%)

### Analytics Dashboard
- Top CPU consumers
- Top memory consumers
- Resource capacity forecast (7 days)
- Regional summary table
- Anomaly detection & alerts

## Performance

### Database Optimization
- Indexes on timestamp, server_id, environment
- Parameterized queries for injection prevention
- Connection pooling with NullPool
- Efficient pagination (default 50 items)

### Frontend Optimization
- Code splitting by route
- Recharts with lazy loading
- Responsive containers (adapts to window size)
- Auto-refresh intervals (30-120 seconds per dashboard)

### Real-time Updates
- WebSocket streaming at 30-second intervals
- Multi-client support with ConnectionManager
- Automatic reconnection handling

## Troubleshooting

### Database Connection Issues
```
Error: could not translate host name
→ Check DB_HOST in .env
→ Verify PostgreSQL is running
→ Check firewall rules
```

### API Connection Issues
```
Error: Failed to fetch from /api/...
→ Verify dashboard-api is running on port 8080
→ Check frontend vite proxy configuration
→ Review CORS settings in FastAPI
```

### Frontend Build Issues
```
Error: Module not found
→ Run: npm install
→ Clear node_modules: rm -rf node_modules && npm install
→ Check package.json dependencies
```

## Monitoring

### Container Health
```bash
# Check container status
docker ps -a

# View container logs
docker logs dashboard-api

# Inspect container details
docker inspect dashboard-frontend
```

### API Health
```bash
# Check API health
curl http://localhost:8080/health

# View API documentation
curl http://localhost:8080/docs
```

### Database Queries
```bash
# Connect to PostgreSQL
psql -h localhost -U postgres -d telemetry

# List tables
\dt

# Check data freshness
SELECT MAX(timestamp) FROM server_metrics;
```

## Deployment Notes

### Production Considerations
- Set `DEBUG=false` in FastAPI
- Use HTTPS with valid certificates
- Implement authentication/authorization
- Setup monitoring and alerting
- Configure log aggregation
- Use environment-specific configurations
- Setup database backups

### Scaling
- Horizontal scaling via Kubernetes
- Load balancing for API (use Nginx/HAProxy)
- Database read replicas for analytics
- Cache layer (Redis) for frequent queries
- CDN for static frontend assets

## File Structure
```
industrial-cloud-data-portfolio/
├── services/
│   ├── generator/
│   ├── ingestion/
│   ├── transformer/
│   └── dashboard-api/
│       ├── main.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       ├── routers/
│       └── Dockerfile
├── dashboard-frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   ├── Dockerfile
│   ├── vite.config.ts
│   └── package.json
├── docker-compose.yml
├── .env
└── test_dashboard_api.py
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review container logs: `docker logs [container-name]`
3. Check API documentation: `http://localhost:8080/docs`
4. Verify environment variables in `.env`

## Version Information

- Python: 3.11
- Node.js: 18
- PostgreSQL: 14
- FastAPI: 0.104.1
- React: 18.2.0
- Recharts: 2.10.3
- Vite: 5.0.0
