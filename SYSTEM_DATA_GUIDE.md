# System Data Guide

## What Data Do We Collect?

We monitor three types of infrastructure data continuously:

### 1. **Server Data**
What we measure about physical servers:
- **CPU usage** (how hard the processor works) → 43% means the processor is doing moderate work
- **Memory usage** (RAM consumption) → 61% means 61% of available RAM is in use
- **Disk space used** → 23% means storage is mostly empty
- **Health status** → healthy/warning/critical based on CPU and memory levels

**Example:**
```
server-01 in us-east-1:
- CPU: 43% → Normal operation ✅
- Memory: 61% → Good headroom left
- Disk: 23% → Plenty of space
- Status: HEALTHY
```

### 2. **Container Data**
What we measure about running applications (Docker containers):
- **CPU usage** → 20% means the app is not using much processor power
- **Memory usage** → 55% means the app has used 55% of allocated RAM
- **Requests per second** (throughput) → 35 means 35 user requests per second
- **Health status** → healthy/degraded/critical based on CPU and requests

**Example:**
```
container-02 running API service:
- CPU: 20% → Light load ✅
- Memory: 55% → Normal usage ✅
- Requests/sec: 35 → Moderate traffic ✅
- Status: DEGRADED (but CPU/memory are fine)
- Note: Degraded might mean slow response times despite low resource use
```

### 3. **Service Data**
What we measure about application performance at the service level:
- **Success rate** (% of requests that work) → 93% means 7 out of 100 requests had issues
- **Error rate** (% that fail) → 3% means 3 out of 100 requests returned errors
- **Response time** (how fast requests are answered) → 297ms is how long the average request takes
- **P95 response time** → 774ms means 95% of requests answer in less than 774ms

**Example:**
```
API Service Performance:
- Success Rate: 93% ⚠️ (target should be 99%+)
- Error Rate: 3% (too high - investigate)
- Avg Response: 297ms (acceptable)
- P95 Response: 774ms (95% of users see responses in under 774ms)
- Total Requests: 1,788,738 processed this week
- Failed Requests: 125,363 need investigation
```

---

## How Data Flows Through the System

```
Generator (creates data every 5 min)
    ↓
Ingestion (saves to storage)
    ↓
Transformer (loads to database every 60 sec)
    ↓
Dashboard API (serves the data via REST endpoints)
    ↓
Frontend (displays in charts/tables)
```

---

## The APIs We Provide

| Endpoint | Returns | Use |
|----------|---------|-----|
| `/api/servers/health` | Overall server health summary | Dashboard widgets |
| `/api/servers/current` | Latest metrics for each server | Servers table |
| `/api/containers/current` | Latest metrics for each container | Containers table |
| `/api/services/performance` | Success rate, response time, errors | Services table |

---

## Why Each Metric Matters

| Metric | Meaning | Good Level | Warning | Critical |
|--------|---------|------------|---------|----------|
| **CPU %** | Processor busy-ness | 20-60% | 70-85% = monitor | > 85% = overloaded |
| **Memory %** | RAM usage | 30-70% | 80-90% = watch it | > 90% = crash risk |
| **Disk %** | Storage used | 20-60% | 70-80% = free space soon | > 85% = emergency |
| **Success Rate** | Requests working | 99%+ | 95-99% = investigate | < 95% = critical |
| **Response Time** | How fast replies come | < 200ms | 200-500ms = slow | > 1000ms = broken |
| **Requests/sec** | Traffic load | 10-50 | 50-80 = monitor load | > 100 = scale now |

### Details for Each Metric:

**CPU Usage Example:**
```
If CPU is 43%:
- Server has 57% available capacity
- Can handle more traffic
- No immediate action needed

If CPU jumps to 88%:
- Server is near maximum
- Response times will slow down
- Need to add more servers within hours
```

**Memory Usage Example:**
```
If Memory is 61%:
- 39% of RAM still available
- Application running smoothly
- Good buffer before issues

If Memory reaches 92%:
- Almost no room left
- Risk of out-of-memory crash
- Must add memory or scale immediately
```

**Success Rate Example:**
```
If Success Rate is 93% (like our API service):
- 1,788,738 total requests processed
- 125,363 requests failed or had errors
- Target is 99.9% (5x better than current)
- Action: Find and fix what's causing 7% failure rate

If Success Rate is 99.5%:
- Operating well
- Some edge cases failing (acceptable)
- Continue monitoring
```

**Response Time Example:**
```
Average Response: 297ms means:
- Most requests answer in ~297 milliseconds
- Fast enough for most users (< 500ms is good)
- Users don't notice slowness

P95 Response: 774ms means:
- 95% of users see responses in < 774ms
- 5% of users wait longer (might be annoyed)
- Slow responses usually happen during traffic spikes
```

**Requests/sec Example:**
```
If Container handles 35 requests/sec:
- Moderate traffic level
- Server not stressed
- Capacity available

If it jumps to 120 requests/sec:
- Very high traffic (maybe viral content?)
- Requests start queuing up
- Response times will increase
- Need to scale to 2+ containers immediately
```

---

## Real-World Scenarios

### Scenario 1: Normal Day
```
Morning 10:00 AM:
✅ Server-01: CPU 35%, Memory 50%, Disk 20%
✅ Container-02: CPU 15%, Memory 45%, 12 req/sec
✅ API Service: 99.2% success rate, 245ms response time

What it means: Everything running smoothly, no action needed
```

### Scenario 2: Traffic Spike
```
Afternoon 2:00 PM (social media post drives traffic):
⚠️ Server-01: CPU 82%, Memory 87%, Disk 20%
⚠️ Container-02: CPU 68%, Memory 76%, 95 req/sec
⚠️ API Service: 96.5% success rate, 892ms response time

What it means: 
- High load, users might notice slowness
- Success rate dropped (some requests timing out)
- NEED TO SCALE: Add another server or container
```

### Scenario 3: After Scaling
```
Same traffic, but now we have 2 servers:
✅ Server-01: CPU 41%, Memory 54%, 48 req/sec
✅ Server-02: CPU 39%, Memory 52%, 47 req/sec
✅ API Service: 99.1% success rate, 320ms response time

What it means:
- Load distributed between servers
- Both servers under healthy load
- Users see fast responses again
- Crisis averted!
```

### Scenario 4: Disk Space Emergency
```
Friday 11:00 PM:
🔴 Server-01: CPU 45%, Memory 65%, Disk 92%
⚠️ Warning: Disk is almost full!

What it means:
- Storage is 92% full
- New files cannot be saved
- Database might become corrupted
- ACTION: Clean up old logs/data immediately

Solution:
- Delete old backups
- Archive old logs to cloud storage
- Delete temporary files
- Monitor closely - if it reaches 99%, server crashes
```

---

## When You Need to Take Action

### 🟢 GREEN (Healthy) - No Action Needed
- CPU: 20-70%
- Memory: 30-80%
- Disk: 20-70%
- Success Rate: > 99%
- Response Time: < 500ms
- Status: All green, system running normally ✅

### 🟡 YELLOW (Warning) - Monitor Closely
- CPU: 70-85%
- Memory: 80-90%
- Disk: 70-85%
- Success Rate: 95-99%
- Response Time: 500-1000ms
- Action: Check logs, be ready to scale

**Example:** "API service is at 98% success rate, we're tracking down that 2% error. Watch closely."

### 🔴 RED (Critical) - Take Action NOW
- CPU: > 85%
- Memory: > 90%
- Disk: > 85%
- Success Rate: < 95%
- Response Time: > 1000ms
- Action: Immediate intervention required

**Example:** "Disk is at 88% full - DELETE OLD DATA NOW or service will crash!"

---

## Quick Decision Guide

### "Should I add more servers?"
**YES if:**
- CPU stays above 80% for more than 10 minutes
- Memory usage exceeds 85%
- Requests per second keeps climbing
- Response time exceeds 1000ms

**Example:** "Container handling 120 req/sec → Add second container"

### "Is my service performing well?"
**YES if:**
- Success rate > 99%
- Response time < 500ms average
- P95 response time < 1 second
- Error rate < 1%

**Example:** "API service at 99.2% success, 297ms avg response = GOOD! 👍"

### "Do I have enough disk space?"
**YES if:**
- Disk usage < 70%

**NO if:**
- Disk usage > 85%
- Free space decreasing weekly
- Need to archive/delete old data

**Example:** "Disk is 92% full - EMERGENCY! Clean up immediately."

