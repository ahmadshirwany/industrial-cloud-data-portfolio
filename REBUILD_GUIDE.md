# Complete Docker Rebuild & Restart Guide

## Purpose
This guide provides step-by-step instructions to completely rebuild all Docker images from scratch, remove old images, and restart all services.

---

## ⚠️ IMPORTANT WARNINGS

1. **Data Loss**: Rebuilding will NOT delete your PostgreSQL data (stored in volumes). Data persists across rebuilds.
2. **Downtime**: Services will be unavailable during the rebuild process (typically 2-3 minutes).
3. **Disk Space**: Rebuilding creates temporary images. Ensure you have at least 2GB free disk space.
4. **Patience**: First rebuild takes longer (5-10 minutes). Subsequent rebuilds are faster (2-3 minutes).

---

## 📋 Pre-Rebuild Checklist

Before running any commands:
- ✅ Ensure Docker Desktop is running
- ✅ Navigate to the project directory: `cd D:\work\industrial-cloud-data-portfolio`
- ✅ Close any browser tabs accessing localhost services
- ✅ Verify PowerShell is open in the project root

---

## 🚀 QUICK REBUILD (Recommended for Most Cases)

Use this if you only modified code, templates, or configuration files:

```powershell
# Step 1: Navigate to project directory
cd D:\work\industrial-cloud-data-portfolio

# Step 2: Stop all running services
docker-compose down

# Step 3: Rebuild all images (no-cache forces complete rebuild)
docker-compose build --no-cache

# Step 4: Start all services
docker-compose up -d

# Step 5: Verify all services are running
docker-compose ps

# Step 6: Check logs for errors (optional)
docker logs dashboard-frontend --tail 5
docker logs dashboard-api --tail 5
```

**Expected Duration**: 2-5 minutes
**What Happens**: Services restart, old containers removed, data persists in database

---

## 🧹 FULL CLEANUP REBUILD (Recommended for Major Changes)

Use this if you want to completely remove all images and start fresh:

```powershell
# Step 1: Navigate to project directory
cd D:\work\industrial-cloud-data-portfolio

# Step 2: Stop all services
docker-compose down

# Step 3: Remove all images for this project
docker rmi industrial-cloud-data-portfolio-dashboard-frontend
docker rmi industrial-cloud-data-portfolio-dashboard-api
docker rmi industrial-cloud-data-portfolio-generator
docker rmi industrial-cloud-data-portfolio-ingestion
docker rmi industrial-cloud-data-portfolio-transformer

# Step 4: Verify images are removed
docker images | findstr industrial-cloud-data-portfolio

# Step 5: Remove unused Docker resources (optional but recommended)
docker system prune -f

# Step 6: Rebuild all images
docker-compose build --no-cache

# Step 7: Start all services
docker-compose up -d

# Step 8: Verify all services are running
docker-compose ps

# Step 9: Check service health (wait 10 seconds first for services to boot)
Start-Sleep 10
docker logs generator --tail 5
docker logs dashboard-api --tail 5
docker logs dashboard-frontend --tail 5
```

**Expected Duration**: 5-10 minutes
**What Happens**: 
- All Docker images deleted
- Database volume preserved
- Fresh images built from scratch
- Services restart with new images

---

## 🔄 REBUILD SPECIFIC SERVICE (For Single Service Changes)

Only rebuild one service when testing individual microservice changes:

```powershell
# Example: Rebuild only the frontend
cd D:\work\industrial-cloud-data-portfolio

# Rebuild and restart frontend
docker-compose build --no-cache dashboard-frontend
docker-compose up -d dashboard-frontend

# Check frontend logs
docker logs dashboard-frontend --tail 10

# Similarly for other services:
# docker-compose build --no-cache dashboard-api
# docker-compose build --no-cache generator
# docker-compose build --no-cache ingestion
# docker-compose build --no-cache transformer
```

---

## 📊 Service Architecture

Understanding what each service does:

| Service | Port | Purpose | Rebuild Impact |
|---------|------|---------|-----------------|
| **generator** | None | Generates telemetry data | Clears in-memory state, keeps DB data |
| **ingestion** | None | Ingests data to GCS | Restarts, keeps GCS data |
| **transformer** | None | Transforms & loads to DB | Restarts, keeps DB tables/data |
| **dashboard-api** | 8080 | Backend API | Restarts, reads from DB |
| **dashboard-frontend** | 8000 | Web UI | Restarts, serves static files |

---

## ✅ VERIFICATION STEPS

After rebuild completes, verify everything is working:

```powershell
# 1. Check all containers are running
docker-compose ps
# Expected: All 5 containers should show "Up"

# 2. Test backend API
Invoke-RestMethod -Uri "http://localhost:8080/api/servers/current?limit=5" -ErrorAction Stop
# Expected: JSON array of server data

# 3. Test frontend home page
# Open browser: http://localhost:8000/
# Expected: Dashboard loads with navigation cards

# 4. Check generator is publishing data
docker logs generator --tail 10
# Expected: Messages like "Publishing metrics every 5 minutes"

# 5. Check for any errors
docker-compose logs --tail 20
# Look for ERROR or CRITICAL messages
```

---

## 🐛 TROUBLESHOOTING

### Issue: "Port already in use"
```powershell
# Solution: Stop conflicting containers
docker-compose down -v
# Remove volumes too if needed (warning: deletes DB!)
# Then rebuild
```

### Issue: "Docker daemon not running"
```powershell
# Solution: Start Docker Desktop
# Wait 30 seconds for it to fully start
# Then run rebuild commands
```

### Issue: "Out of disk space"
```powershell
# Solution: Clean up Docker
docker system prune -a --volumes
# Then rebuild
```

### Issue: "Services not responding"
```powershell
# Solution: Check service logs
docker logs <service-name> --tail 20
# Common services: generator, dashboard-api, dashboard-frontend
# Look for ERROR messages
```

### Issue: "Database connection errors"
```powershell
# The database persists in Docker volumes
# Usually these errors are temporary during startup
# Wait 20 seconds and refresh browser
```

---

## 📝 COMMAND REFERENCE

**Quick Reference for Common Tasks**:

```powershell
# View all running containers
docker-compose ps

# View logs for a service
docker logs <service-name>

# View live logs (follow mode)
docker logs -f <service-name>

# Stop all services (keeps volumes/data)
docker-compose down

# Stop and remove volumes (DELETES DATABASE!)
docker-compose down -v

# Restart services without rebuilding
docker-compose up -d

# Rebuild all without starting
docker-compose build --no-cache

# Start after rebuild
docker-compose up -d

# Check which images exist
docker images | findstr industrial

# Remove specific image
docker rmi <image-name>

# Access service shell (for debugging)
docker exec -it <container-name> bash
```

---

## 🎯 COMMON SCENARIOS

### Scenario 1: I modified frontend templates
```powershell
cd D:\work\industrial-cloud-data-portfolio
docker-compose build --no-cache dashboard-frontend
docker-compose up -d dashboard-frontend
docker logs dashboard-frontend --tail 5
```

### Scenario 2: I modified generator settings
```powershell
cd D:\work\industrial-cloud-data-portfolio
docker-compose build --no-cache generator
docker-compose up -d generator
docker logs generator --tail 5
```

### Scenario 3: I modified API routes
```powershell
cd D:\work\industrial-cloud-data-portfolio
docker-compose build --no-cache dashboard-api
docker-compose up -d dashboard-api
docker logs dashboard-api --tail 5
```

### Scenario 4: Everything is broken, start fresh
```powershell
cd D:\work\industrial-cloud-data-portfolio
docker-compose down
docker rmi industrial-cloud-data-portfolio-dashboard-frontend
docker rmi industrial-cloud-data-portfolio-dashboard-api
docker rmi industrial-cloud-data-portfolio-generator
docker rmi industrial-cloud-data-portfolio-ingestion
docker rmi industrial-cloud-data-portfolio-transformer
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
Start-Sleep 15
docker-compose ps
```

---

## ⏱️ TIMING GUIDE

**First Rebuild** (initial setup or full cleanup):
- Download base images: 1-2 min
- Install dependencies: 3-5 min
- Build each service: 2-3 min
- Start containers: 30 sec
- **Total: 7-12 minutes**

**Subsequent Rebuilds** (code changes only):
- Build cached services: 1-2 min
- Start containers: 30 sec
- **Total: 2-3 minutes**

---

## 📞 GETTING HELP

If rebuild fails:

1. **Check the error message** - Docker will tell you what failed
2. **View full logs** - `docker-compose logs` shows all service logs
3. **Check disk space** - `dir D:\` and verify >2GB free
4. **Check Docker status** - Open Docker Desktop GUI to verify it's running
5. **Try the cleanup rebuild** - Sometimes `docker system prune -a` helps

---

## 🔐 DATA SAFETY

Your data is safe during rebuild because:
- Database volumes are separate from images
- `docker-compose down` only stops containers, doesn't delete volumes
- `docker-compose up -d` restarts and reconnects to existing volumes
- Use `-v` flag only if you explicitly want to delete data

---

## 🎓 LEARNING TIPS

- `docker-compose ps` is your friend - run this first to check status
- `docker logs <service>` shows what's happening inside containers
- Rebuilds are safe to try multiple times
- Check file ownership if permission denied errors appear
- Patience! First rebuild takes longer due to downloading base images

---

**Last Updated**: December 22, 2025
**Project**: Industrial Cloud Data Portfolio Dashboard
**Docker Compose Version**: 2.x
