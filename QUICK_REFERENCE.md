# Quick Reference Guide

## 🚀 Quick Start

```bash
# 1. Navigate to project root
cd /path/to/industrial-cloud-data-portfolio

# 2. Create .env file (if not exists)
# Copy example below and fill in your values

# 3. Start all services
docker-compose up --build

# 4. Access dashboards
# Frontend: http://localhost:5173
# API Docs: http://localhost:8080/docs
```

## 📋 Essential Commands

### Docker Commands
```bash
# Start services in background
docker-compose up -d --build

# View logs
docker-compose logs -f [service-name]

# Stop all services
docker-compose down

# Remove everything (containers + volumes)
docker-compose down -v

# List running services
docker-compose ps

# Execute command in running container
docker-compose exec dashboard-api python -c "..."
```

### Frontend Commands
```bash
cd dashboard-frontend

# Development server (with API proxy)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Run tests
npm run test
```

### Backend Commands
```bash
cd services/dashboard-api

# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn main:app --reload --port 8080

# Run tests
python -m pytest
```

## 🔧 Environment Setup (.env)

Create a `.env` file in the project root:

```env
# Database Configuration
DB_HOST=localhost
DB_NAME=telemetry
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_PORT=5432

# Google Cloud Configuration
GCP_PROJECT_ID=your-gcp-project-id
GCP_BUCKET_NAME=your-telemetry-bucket
GOOGLE_APPLICATION_CREDENTIALS=/app/config/service-account.json
```

## 📊 Available Endpoints

### Servers
- `GET /api/servers/health` - Health status summary
- `GET /api/servers/current?limit=50` - Current metrics
- `GET /api/servers/trends/cpu?hours=24&interval=15min` - CPU trends
- `GET /api/servers/by-region` - Regional distribution
- `GET /api/servers/top-cpu?limit=10` - Top CPU consumers
- `GET /api/servers/disk-usage` - Disk metrics

### Containers
- `GET /api/containers/health?minutes=5` - Health summary
- `GET /api/containers/current?limit=50` - Current containers
- `GET /api/containers/by-service` - Grouped by service
- `GET /api/containers/high-memory?threshold=80&limit=20` - High memory
- `GET /api/containers/restarts` - Restart statistics
- `GET /api/containers/throughput-trend?hours=24` - Throughput trends

### Services
- `GET /api/services/performance?hours=1` - Performance metrics
- `GET /api/services/latency-trend?hours=24` - Latency over time
- `GET /api/services/error-rate-trend?hours=24` - Error rates
- `GET /api/services/success-rate?minutes=5` - Success rate
- `GET /api/services/failed-requests?hours=24` - Failed requests
- `GET /api/services/instances` - Service instances
- `GET /api/services/by-region` - Regional distribution
- `GET /api/services/slowest?limit=5` - Slowest services

### Analytics
- `GET /api/analytics/system-health?minutes=5` - Overall health
- `GET /api/analytics/top-cpu-resources?limit=5` - Top CPU
- `GET /api/analytics/top-memory-resources?limit=5` - Top memory
- `GET /api/analytics/anomalies?hours=1` - Anomaly detection
- `GET /api/analytics/daily-stats` - 24-hour statistics
- `GET /api/analytics/capacity-forecast?days=7` - Capacity forecast
- `GET /api/analytics/regional-summary` - Regional summary

### WebSocket
- `WS /api/ws/metrics` - Real-time metric streaming

## 🎨 Dashboard Views

| View | Features | Refresh Rate |
|------|----------|--------------|
| **Overview** | System health, KPIs, resource trends | 30 seconds |
| **Servers** | Health status, CPU/disk trends, top consumers | 60 seconds |
| **Services** | Performance, latency, error rates, failures | 60 seconds |
| **Containers** | Health, memory, throughput, restarts | 60 seconds |
| **Analytics** | Anomalies, forecasts, capacity, regional data | 120 seconds |

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs dashboard-api

# Common issues:
# - Port already in use: Change port in docker-compose.yml
# - Database not ready: Wait 30 seconds and try again
# - Image build failed: Run with --no-cache
docker-compose up --build --no-cache
```

### API Connection Failed
```bash
# Verify API is running
curl http://localhost:8080/health

# Check logs
docker-compose logs dashboard-api

# Verify database connection
docker-compose exec dashboard-api python -c "from database import engine; engine.connect()"
```

### Frontend Not Loading
```bash
# Verify frontend is running
curl http://localhost:5173

# Check logs
docker-compose logs dashboard-frontend

# For development, check vite logs
npm run dev
```

### Database Issues
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d telemetry

# Check table structure
\dt
\d server_metrics

# Check latest data
SELECT MAX(timestamp) FROM server_metrics;
SELECT COUNT(*) FROM server_metrics;
```

## 📈 Performance Tips

1. **Frontend Optimization**
   - Recharts auto-scales based on window size
   - Lazy loading for off-screen content
   - Query data pagination (default 50 items)

2. **API Optimization**
   - Use `limit` parameter to reduce data transfer
   - Specify `hours`/`minutes` for time-based queries
   - Indexed columns: timestamp, server_id, environment

3. **Database Optimization**
   - Indexes on frequently queried columns
   - Parameterized queries prevent SQL injection
   - Connection pooling reduces overhead

## 🔐 Security Notes

- [ ] Change default database password
- [ ] Setup HTTPS/SSL certificates
- [ ] Implement API authentication (JWT tokens)
- [ ] Setup firewall rules
- [ ] Enable database encryption
- [ ] Rotate GCP service account keys regularly
- [ ] Use environment variables for sensitive data

## 📝 Log Locations

```bash
# Docker container logs
docker-compose logs [service-name]

# Application logs (in containers)
/var/log/[service-name].log

# Database logs
docker-compose logs postgres

# Frontend development
npm run dev  # Shows in terminal
```

## 🔄 Data Refresh Intervals

| Service | Interval | Operation |
|---------|----------|-----------|
| Generator | 30 sec | Generate synthetic data |
| Ingestion | Real-time | Consume from Pub/Sub |
| Transformer | 60 sec | ETL to database |
| Dashboard | 30-120 sec | Fetch and display data |
| WebSocket | 30 sec | Stream real-time metrics |

## 🎯 Key Metrics

Each dashboard tracks:

**Servers Dashboard**
- CPU, Memory, Disk utilization
- Request count, Error count
- Response time, Status

**Services Dashboard**
- Latency (P50, P95, P99)
- Error rate, Success rate
- Throughput (RPS)

**Containers Dashboard**
- Memory usage, CPU usage
- Restart count, Uptime
- Network I/O, Disk I/O

**Analytics Dashboard**
- Anomalies (real-time detection)
- Resource forecast (7-day projection)
- Regional distribution
- Capacity planning

## 💡 Tips & Tricks

### View Real-time Data
```bash
# Watch API responses
watch -n 5 "curl -s http://localhost:8080/api/servers/health | jq"

# Stream WebSocket data
# Use browser DevTools → Network → WS
```

### Test API Endpoints
```bash
# Using curl
curl http://localhost:8080/api/servers/health

# Using Python
python -c "
import requests
r = requests.get('http://localhost:8080/api/servers/health')
print(r.json())
"

# Using the test script
python test_dashboard_api.py
```

### Debug Frontend
```bash
# Open browser DevTools (F12)
# Network tab: Check API requests
# Console tab: Check for errors
# Application tab: Check local storage

# Development mode
npm run dev  # With detailed output
```

## 📚 Additional Resources

- FastAPI Docs: http://localhost:8080/docs (when running)
- React Docs: https://react.dev
- Recharts Docs: https://recharts.org
- Tailwind Docs: https://tailwindcss.com

## ✅ Verification Checklist

After startup, verify:
- [ ] Docker Compose up: `docker-compose ps`
- [ ] Frontend loads: http://localhost:5173
- [ ] API responds: http://localhost:8080/health
- [ ] Database ready: Check logs for connection
- [ ] API Docs: http://localhost:8080/docs
- [ ] Dashboard displays data
- [ ] All 5 views load correctly
- [ ] Charts render without errors

## 🎓 Learning Resources

1. Start with Overview Dashboard to understand system health
2. Check Servers Dashboard for infrastructure monitoring
3. Review Services Dashboard for application performance
4. Analyze Containers Dashboard for container health
5. Use Analytics Dashboard for forecasting and anomalies

## 📞 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Port 8080 in use | Change in docker-compose.yml |
| Port 5173 in use | Change in docker-compose.yml |
| Database won't connect | Check .env values, wait for DB to start |
| API returns 500 error | Check logs: `docker-compose logs dashboard-api` |
| Frontend shows 404 | Verify frontend is running, check proxy config |
| Charts not rendering | Check browser console for errors |
| Real-time data not updating | Check WebSocket connection in DevTools |

---

**Last Updated**: 2024
**Version**: 1.0
**Status**: Production Ready ✅
