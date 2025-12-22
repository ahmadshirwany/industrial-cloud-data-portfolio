# Dashboard API Documentation

## Overview
FastAPI backend service providing REST APIs and WebSocket support for the industrial telemetry dashboard.

## Base URL
- **Local Development**: `http://localhost:8080`
- **Docker**: `http://localhost:8080`

## API Documentation
- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

---

## Server Metrics Endpoints

### 1. Get Server Health Summary
**GET** `/api/servers/health`

Get aggregated health status of all servers.

**Query Parameters:**
- `minutes` (int, default: 5) - Time window in minutes

**Response:**
```json
{
  "total_servers": 50,
  "healthy_servers": 45,
  "warning_servers": 3,
  "critical_servers": 2,
  "avg_cpu": 65.2,
  "avg_memory": 72.5,
  "avg_disk": 45.8
}
```

### 2. Get Current Server States
**GET** `/api/servers/current`

Get latest metrics for all servers.

**Query Parameters:**
- `limit` (int, default: 50, max: 100)

**Response:**
```json
[
  {
    "timestamp": "2024-01-15T10:30:00",
    "server_id": "server-001",
    "cpu_percent": 78.5,
    "memory_percent": 82.3,
    "disk_utilization": 55.0,
    "status": "warning",
    "region": "us-east-1"
  }
]
```

### 3. Get CPU Trends
**GET** `/api/servers/trends/cpu`

Time-series data for CPU, memory, and disk utilization.

**Query Parameters:**
- `hours` (int, default: 24, max: 168)
- `interval` (str, default: "5min") - Options: "5min", "15min", "1hour"

**Response:**
```json
[
  {
    "time": "2024-01-15T10:00:00",
    "avg_cpu": 65.2,
    "avg_memory": 70.5,
    "avg_disk": 45.0
  }
]
```

### 4. Get Servers by Region
**GET** `/api/servers/by-region`

Regional aggregation of server metrics.

**Response:**
```json
[
  {
    "region": "us-east-1",
    "server_count": 20,
    "avg_cpu": 65.2,
    "avg_memory": 72.0
  }
]
```

### 5. Get Top CPU Consumers
**GET** `/api/servers/top-cpu`

Servers with highest CPU usage.

**Query Parameters:**
- `limit` (int, default: 10, max: 50)

**Response:**
```json
[
  {
    "server_id": "server-042",
    "cpu_percent": 95.3,
    "memory_percent": 88.2,
    "status": "critical"
  }
]
```

### 6. Get Disk Usage
**GET** `/api/servers/disk-usage`

Servers with disk usage > 50%.

**Response:**
```json
[
  {
    "server_id": "server-015",
    "disk_utilization": 78.5,
    "status": "warning"
  }
]
```

---

## Container Metrics Endpoints

### 1. Get Container Health
**GET** `/api/containers/health`

Container health summary.

**Query Parameters:**
- `minutes` (int, default: 5)

**Response:**
```json
{
  "total_containers": 200,
  "healthy_containers": 185,
  "degraded_containers": 10,
  "unhealthy_containers": 5,
  "avg_memory_utilization": 68.5,
  "total_restarts": 12
}
```

### 2. Get Current Containers
**GET** `/api/containers/current`

Latest state of all containers.

**Query Parameters:**
- `limit` (int, default: 50, max: 100)

### 3. Get Containers by Service
**GET** `/api/containers/by-service`

Group containers by service name.

### 4. Get High Memory Containers
**GET** `/api/containers/high-memory`

Containers exceeding memory threshold.

**Query Parameters:**
- `threshold` (float, default: 80.0)
- `limit` (int, default: 20, max: 50)

### 5. Get Container Restarts
**GET** `/api/containers/restarts`

Containers with restart activity.

**Query Parameters:**
- `hours` (int, default: 24)

### 6. Get Throughput Trend
**GET** `/api/containers/throughput-trend`

Requests per second over time.

**Query Parameters:**
- `hours` (int, default: 24, max: 168)

---

## Service Metrics Endpoints

### 1. Get Service Performance
**GET** `/api/services/performance`

Performance metrics for all services.

**Query Parameters:**
- `hours` (int, default: 1)

**Response:**
```json
[
  {
    "service_name": "api-gateway",
    "avg_success_rate": 99.2,
    "avg_error_rate": 0.8,
    "avg_response_time": 125.5,
    "p95_response_time": 320.0,
    "total_requests": 45000,
    "failed_requests": 360
  }
]
```

### 2. Get Latency Trend
**GET** `/api/services/latency-trend`

Response time trends by service.

**Query Parameters:**
- `hours` (int, default: 24, max: 168)

### 3. Get Error Rate Trend
**GET** `/api/services/error-rate-trend`

Error rate over time.

### 4. Get Success Rate Gauge
**GET** `/api/services/success-rate-gauge`

Current success rate (for gauge charts).

**Query Parameters:**
- `minutes` (int, default: 5)

### 5. Get Failed Requests
**GET** `/api/services/failed-requests`

Total failures by service.

**Query Parameters:**
- `hours` (int, default: 24)

### 6. Get Service Instances
**GET** `/api/services/instances`

Running instance count per service.

### 7. Get Services by Region
**GET** `/api/services/by-region`

Service performance grouped by region.

### 8. Get Slowest Services
**GET** `/api/services/slowest`

Services with highest latency.

**Query Parameters:**
- `limit` (int, default: 10, max: 50)

---

## Analytics Endpoints

### 1. Get System Health Score
**GET** `/api/analytics/system-health`

Overall system health (0-100).

**Query Parameters:**
- `minutes` (int, default: 5)

**Response:**
```json
{
  "score": 87.5,
  "avg_cpu": 65.2,
  "avg_memory": 72.0,
  "avg_disk": 45.5,
  "avg_success_rate": 99.1,
  "critical_servers": 2
}
```

### 2. Get Top CPU Resources
**GET** `/api/analytics/top-cpu-resources`

Top CPU consumers across all servers.

**Query Parameters:**
- `limit` (int, default: 10, max: 50)

### 3. Get Top Memory Resources
**GET** `/api/analytics/top-memory-resources`

Top memory consumers (servers + containers).

**Query Parameters:**
- `limit` (int, default: 10, max: 50)

### 4. Detect Anomalies
**GET** `/api/analytics/anomalies`

Detect CPU spikes, memory pressure, error spikes.

**Query Parameters:**
- `hours` (int, default: 1)

**Response:**
```json
[
  {
    "resource_name": "server-042",
    "anomaly_type": "cpu_spike",
    "value": 95.3,
    "timestamp": "2024-01-15T10:30:00",
    "severity": "high"
  }
]
```

### 5. Get Daily Stats
**GET** `/api/analytics/daily-stats`

24-hour aggregated statistics.

**Response:**
```json
{
  "avg_cpu": 65.2,
  "avg_memory": 72.0,
  "avg_disk": 45.5,
  "total_servers": 50,
  "total_requests": 1250000,
  "failed_requests": 10000,
  "avg_success_rate": 99.2,
  "total_restarts": 45,
  "active_containers": 200
}
```

### 6. Get Capacity Forecast
**GET** `/api/analytics/capacity-forecast`

Resource growth forecast.

**Query Parameters:**
- `days` (int, default: 7, max: 30)

### 7. Get Regional Summary
**GET** `/api/analytics/regional-summary`

Summary metrics by region.

---

## WebSocket Endpoint

### Real-time Metrics Stream
**WS** `/ws/metrics`

Streams real-time metrics every 30 seconds.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8080/ws/metrics');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

**Message Format:**
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "servers": {
    "total": 50,
    "avg_cpu": 65.2,
    "avg_memory": 72.0,
    "avg_disk": 45.5,
    "healthy": 45,
    "warning": 3,
    "critical": 2
  },
  "containers": {
    "total": 200,
    "avg_memory": 68.5,
    "avg_rps": 1250.5,
    "healthy": 185,
    "total_restarts": 12
  },
  "services": {
    "total": 15,
    "avg_success_rate": 99.2,
    "avg_error_rate": 0.8,
    "avg_latency": 125.5,
    "total_requests": 50000
  }
}
```

### Get Active Connections
**GET** `/ws/connections`

Get count of active WebSocket clients.

**Response:**
```json
{
  "active_connections": 5,
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## Error Responses

All endpoints return standard HTTP error codes:

**400 Bad Request**
```json
{
  "detail": "Invalid parameter: minutes must be > 0"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Database connection failed"
}
```

---

## Rate Limiting
No rate limiting implemented (suitable for internal dashboard use).

## CORS
CORS is enabled for all origins (`allow_origins=["*"]`). Configure in production.

## Authentication
No authentication implemented. Add JWT/OAuth for production deployment.

---

## Running the Service

### Docker Compose
```bash
docker-compose up dashboard-api
```

### Local Development
```bash
cd services/dashboard-api
pip install -r requirements.txt
uvicorn services.dashboard_api.main:app --reload --port 8080
```

### Access Documentation
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

---

## Environment Variables

Required environment variables (set in `.env`):
```
DB_HOST=your-postgres-host
DB_NAME=telemetry
DB_USER=your-username
DB_PASSWORD=your-password
DB_PORT=5432
```

---

## Chart Types Supported

**Time-Series Charts:**
- CPU/Memory/Disk trends (`/api/servers/trends/cpu`)
- Service latency trends (`/api/services/latency-trend`)
- Error rate trends (`/api/services/error-rate-trend`)
- Throughput trends (`/api/containers/throughput-trend`)

**Gauge Charts:**
- System health score (`/api/analytics/system-health`)
- Success rate gauge (`/api/services/success-rate-gauge`)

**Bar/Column Charts:**
- Servers by region (`/api/servers/by-region`)
- Top CPU consumers (`/api/servers/top-cpu`)
- Slowest services (`/api/services/slowest`)

**Pie/Donut Charts:**
- Server health distribution (`/api/servers/health`)
- Container health distribution (`/api/containers/health`)

**Table/Grid:**
- Current servers (`/api/servers/current`)
- Anomalies list (`/api/analytics/anomalies`)
- Container restarts (`/api/containers/restarts`)

**Heatmap:**
- Regional summary (`/api/analytics/regional-summary`)

---

## Testing

Test endpoints with curl:
```bash
# Health check
curl http://localhost:8080/health

# Get server health
curl http://localhost:8080/api/servers/health?minutes=5

# Get system health score
curl http://localhost:8080/api/analytics/system-health

# Test WebSocket (using websocat)
websocat ws://localhost:8080/ws/metrics
```
