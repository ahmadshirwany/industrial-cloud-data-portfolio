# Testing Guide

Quick guide to test the complete application system.

## 3 Essential Tests

Run these 3 tests to verify everything is working:

### Test 1: System Health (Docker & Services)

Check if all Docker containers are running and responding:

```powershell
python test_system_health.py
```

**What it tests:**
- ✅ All 5 Docker containers are running
- ✅ API server responding on port 8080
- ✅ Frontend server responding on port 8000
- ✅ Data generator is active

**Expected output:**
```
✅ All services are running
✅ API responding
✅ Frontend responding
✅ Generator is active
```

---

### Test 2: API Endpoints

Test all REST API endpoints:

```powershell
python test_api_health.py
```

**What it tests:**
- ✅ Server metrics endpoints
- ✅ Container metrics endpoints
- ✅ Service metrics endpoints
- ✅ Analytics endpoints

**Expected output:**
```
✅ 5 records     /servers/current?limit=5
✅ 10 records    /servers/history?hours=1&limit=10
✅ 5 records     /containers/current?limit=5
✅ OK            /containers/health
✅ 5 records     /services/current?limit=5
✅ OK            /analytics/cpu-trends?hours=6
✅ OK            /analytics/memory-trends?hours=6
✅ OK            /analytics/health-score

Result: 8/8 endpoints working
```

---

### Test 3: Dashboard Pages

Test if all dashboard pages load:

```powershell
python test_dashboard.py
```

**What it tests:**
- ✅ Home page loads
- ✅ Dashboard page loads
- ✅ Servers tab loads
- ✅ Containers tab loads
- ✅ Profile page loads
- ✅ Database has data

**Expected output:**
```
✅ Loaded              /
✅ Loaded              /dashboard
✅ Loaded              /servers
✅ Loaded              /containers
✅ Loaded              /profile

✅ Database has data    5 server records found

Result: 5/5 pages loaded
```

---

## Quick Test Sequence

Run these commands in order to verify complete system:

```powershell
# 1. Verify all services are up
python test_system_health.py

# 2. Test API is working
python test_api_health.py

# 3. Test dashboard pages
python test_dashboard.py
```

---

## How to Use Results

**All tests pass? ✅**
- System is fully operational
- Ready to use dashboard
- Safe to make changes

**Some tests fail? ⚠️**

1. **System health fails**
   - Check Docker Desktop is running
   - Run: `docker-compose ps`
   - Run: `docker-compose up -d`

2. **API tests fail**
   - Check logs: `docker logs dashboard-api --tail 10`
   - Restart API: `docker-compose restart dashboard-api`

3. **Dashboard tests fail**
   - Check logs: `docker logs dashboard-frontend --tail 10`
   - Restart frontend: `docker-compose restart dashboard-frontend`

---

## Common Issues

### "Cannot connect to API"
```powershell
# Check if API is running
docker ps | findstr dashboard-api

# If not running, start it
docker-compose up -d dashboard-api

# Wait 5 seconds and test again
Start-Sleep 5
python test_api_health.py
```

### "Cannot connect to frontend"
```powershell
# Check if frontend is running
docker ps | findstr dashboard-frontend

# If not running, start it
docker-compose up -d dashboard-frontend

# Wait 5 seconds and test again
Start-Sleep 5
python test_dashboard.py
```

### "Database empty"
```powershell
# Check if generator is running
docker logs generator --tail 5

# Generator publishes every 5 minutes
# Wait a few minutes and test again
```

---

## What Each Test Tests

| Test | Purpose | Duration |
|------|---------|----------|
| test_system_health.py | Docker & service availability | ~5 sec |
| test_api_health.py | API endpoint functionality | ~8 sec |
| test_dashboard.py | Frontend page loading | ~7 sec |

**Total test time: ~20 seconds**

---

## Manual Testing

If you prefer to test manually:

### Check Docker
```powershell
docker-compose ps
```

### Test API with Browser
Open: http://localhost:8080/api/servers/current?limit=5

### Test Frontend with Browser
Open: http://localhost:8000/

### Check Logs
```powershell
# All services
docker-compose logs --tail 20

# Specific service
docker logs generator --tail 10
docker logs dashboard-api --tail 10
docker logs dashboard-frontend --tail 10
```

---

**Last Updated**: December 22, 2025
