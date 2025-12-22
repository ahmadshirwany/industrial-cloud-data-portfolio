# Quick Navigation Guide

Use this guide to find the right documentation for your needs.

## 🚀 I'm New - Where Do I Start?

1. **[README.md](README.md)** (5 min read)
   - What is this project?
   - What features does it have?
   - Technology overview

2. **[SETUP.md](SETUP.md)** (10 min read)
   - How do I install it?
   - How do I run it?
   - How do I verify it works?

3. **Access the Dashboard**
   - Frontend: http://localhost:8000
   - API docs: http://localhost:8080/docs

## ✅ I Want to Test Everything

Run the test suite to verify all systems are working:

```powershell
# Test 1: System health (Docker, API, Frontend, Generator) - ~5 sec
& .venv\Scripts\python.exe test_system_health.py

# Test 2: API endpoints (5 critical endpoints) - ~5 sec
& .venv\Scripts\python.exe test_api_health.py

# Test 3: Dashboard pages (5 pages + database data) - ~5 sec
& .venv\Scripts\python.exe test_dashboard.py
```

**Expected Results:**
- ✅ 4/4 tests passing (System health)
- ✅ 5/5 endpoints passing (API)
- ✅ 5/5 pages loaded (Dashboard)

See [TESTING.md](TESTING.md) for detailed test guide.

## 🔧 I Want to Make Changes

1. **Modify code/templates**
   - Edit files in `services/` folders
   - Frontend templates: `services/dashboard-frontend/templates/`
   - Backend routes: `services/dashboard-api/routers/`

2. **Test your changes**
   - Run tests to verify nothing broke (see above)

3. **Rebuild affected service**
   - See [REBUILD_GUIDE.md](REBUILD_GUIDE.md)
   - Quick rebuild: 2-5 minutes
   - Full cleanup: 5-10 minutes

## 📦 Everything Broke - Help!

1. **Check the logs**
   ```powershell
   docker-compose logs --tail 50
   ```

2. **See troubleshooting section in [SETUP.md](SETUP.md)**
   - Common issues
   - Solutions
   - Verification steps

3. **Rebuild everything fresh**
   - See "FULL CLEANUP REBUILD" in [REBUILD_GUIDE.md](REBUILD_GUIDE.md)

## 🏗️ Understanding the Project

**Project Structure** (see [README.md](README.md))
```
Frontend (8000) ←→ API (8080) ←→ Database
     ↓
Templates & Static Files
```

**Data Flow** (see [README.md](README.md))
```
Generator → GCP Pub/Sub → Ingestion → Storage
                            ↓
                      Transformer → PostgreSQL
                            ↓
                        Dashboard API
```

## 📚 Documentation Files

| File | Purpose | Read Time |
|------|---------|-----------|
| [README.md](README.md) | Project overview | 5 min |
| [SETUP.md](SETUP.md) | Installation & config | 10 min |
| [TESTING.md](TESTING.md) | Test suite guide | 5 min |
| [REBUILD_GUIDE.md](REBUILD_GUIDE.md) | Docker commands | 15 min |
| [CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md) | Changes made | 5 min |

## 🔍 Find Commands Reference

**Starting services:**
```powershell
docker-compose up -d
```

**Stopping services:**
```powershell
docker-compose down
```

**Checking status:**
```powershell
docker-compose ps
```

**Viewing logs:**
```powershell
docker logs <service-name> --tail 10
```

See [REBUILD_GUIDE.md](REBUILD_GUIDE.md) for complete command reference.

## 📞 Need Help?

1. **Something not working?** → Run tests first (see "I Want to Test Everything" above)
2. **Can't start services?** → See [SETUP.md](SETUP.md) troubleshooting
3. **Need Docker commands?** → See [REBUILD_GUIDE.md](REBUILD_GUIDE.md)
4. **Want to know the tech?** → See [README.md](README.md)
5. **What changed?** → See [CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md)

---

**Pro Tip**: Bookmark [SETUP.md](SETUP.md) for the most common operations!
