# Dashboard API Testing Instructions

## Prerequisites

1. **Start the Dashboard API service:**
   ```powershell
   docker-compose up dashboard-api
   ```

2. **Install test dependencies (in a separate terminal):**
   ```powershell
   pip install requests
   ```

## Running the Tests

### Option 1: Run Test Script Directly
```powershell
python test_dashboard_api.py
```

### Option 2: Run from Project Root
```powershell
cd d:\work\industrial-cloud-data-portfolio
python test_dashboard_api.py
```

## What the Test Script Does

The test script will:

1. ✅ Test all 37 API endpoints
2. 📊 Display formatted responses with colors
3. ⏱️ Show response times for each endpoint
4. 📈 Provide a summary with pass/fail counts
5. 🎨 Use color-coded output:
   - 🟢 Green = Success
   - 🔴 Red = Failed
   - 🔵 Blue = Response data
   - 🟡 Yellow = Warnings
   - 🟣 Purple = Headers

## Expected Output

```
================================================================================
                        DASHBOARD API TEST SUITE
================================================================================

ℹ Testing API at: http://localhost:8080
ℹ Started at: 2025-12-18 10:30:00

================================================================================
                            BASIC ENDPOINTS
================================================================================

Testing: Root endpoint
Endpoint: GET /
Status Code: 200
Response Time: 45.23ms
Response:
{
  "service": "Dashboard API",
  "status": "running"
}
✓ PASSED - Root endpoint

Testing: Health check
Endpoint: GET /health
Status Code: 200
Response Time: 12.45ms
Response:
{
  "status": "healthy"
}
✓ PASSED - Health check

================================================================================
                        SERVER METRICS ENDPOINTS
================================================================================

Testing: Get server health summary
Endpoint: GET /api/servers/health
Parameters: {'minutes': 5}
Status Code: 200
Response Time: 156.78ms
Response:
{
  "total_servers": 50,
  "healthy_servers": 45,
  "warning_servers": 3,
  "critical_servers": 2,
  "avg_cpu": 65.2,
  "avg_memory": 72.5,
  "avg_disk": 45.8
}
✓ PASSED - Get server health summary

[... more tests ...]

================================================================================
                            TEST SUMMARY
================================================================================

Total Tests: 37
✓ Passed: 37
✗ Failed: 0

Success Rate: 100.0%

🎉 ALL TESTS PASSED! 🎉

================================================================================

ℹ Test WebSocket streaming:
ws://localhost:8080/ws/metrics
ℹ Use a WebSocket client like 'websocat' or browser DevTools

API Documentation:
Swagger UI: http://localhost:8080/docs
ReDoc: http://localhost:8080/redoc
```

## Troubleshooting

### Error: Cannot connect to http://localhost:8080
**Solution:** Make sure dashboard-api service is running:
```powershell
docker-compose up dashboard-api
```

### Error: No data returned (empty responses)
**Solution:** Wait for the transformer service to populate the database:
```powershell
# Check if data exists
docker-compose logs transformer
```

### Error: Import error - No module named 'requests'
**Solution:** Install the requests library:
```powershell
pip install requests
```

### Test timeout errors
**Solution:** Increase the TIMEOUT value in test script (default: 10 seconds)

## Testing Individual Endpoints

You can also test individual endpoints using curl:

```powershell
# Health check
curl http://localhost:8080/health

# Server health
curl "http://localhost:8080/api/servers/health?minutes=5"

# System health score
curl "http://localhost:8080/api/analytics/system-health?minutes=5"

# Top CPU consumers
curl "http://localhost:8080/api/servers/top-cpu?limit=5"
```

## Testing WebSocket

### Using Python (websockets library):
```powershell
pip install websockets
```

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8080/ws/metrics"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        
        # Receive 3 messages
        for i in range(3):
            message = await websocket.recv()
            data = json.loads(message)
            print(f"\nMessage {i+1}:")
            print(json.dumps(data, indent=2))

asyncio.run(test_websocket())
```

### Using websocat (command-line tool):
```powershell
# Install websocat first
# Download from: https://github.com/vi/websocat/releases

websocat ws://localhost:8080/ws/metrics
```

### Using Browser DevTools:
```javascript
// Open browser console and run:
const ws = new WebSocket('ws://localhost:8080/ws/metrics');

ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
ws.onerror = (error) => console.error('Error:', error);
```

## Next Steps

After testing completes successfully:

1. ✅ All APIs are working
2. 🎯 Ready for frontend development
3. 📊 Use the API responses to design dashboard charts
4. 🔌 Integrate WebSocket for real-time updates
5. 📖 Reference API_DOCUMENTATION.md for endpoint details

## Continuous Testing

Run tests after any changes:
```powershell
# Restart service
docker-compose restart dashboard-api

# Wait 5 seconds for startup
Start-Sleep -Seconds 5

# Run tests
python test_dashboard_api.py
```

## Performance Benchmarking

The test script shows response times. Typical values:
- Basic endpoints: < 50ms
- Simple queries: 50-200ms
- Complex aggregations: 200-500ms
- Time-series queries: 500-1000ms

If response times are consistently high (>2s), check:
- Database indexes
- PostgreSQL connection pool
- Network latency to Cloud SQL
