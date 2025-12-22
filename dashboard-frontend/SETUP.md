# Frontend Setup Guide

## Prerequisites

### 1. Install Node.js

Your system doesn't have Node.js installed yet. Follow these steps:

**Option A: Download and Install (Recommended)**
1. Go to https://nodejs.org/
2. Download the **LTS (Long Term Support)** version (18.x or 20.x)
3. Run the installer and follow the prompts
4. **Important**: Check the box "Add to PATH" during installation
5. Restart any open terminal windows

**Option B: Use Windows Package Manager**
```powershell
# If you have Windows Package Manager installed:
winget install OpenJS.NodeJS

# Verify installation
node --version
npm --version
```

**Option C: Use Chocolatey**
```powershell
# If you have Chocolatey installed:
choco install nodejs

# Verify installation
node --version
npm --version
```

After installation, restart PowerShell and verify:
```powershell
node --version  # Should show v18.x.x or later
npm --version   # Should show 9.x.x or later
```

---

## Quick Start (After Node.js is Installed)

### Step 1: Navigate to Frontend Directory
```powershell
cd d:\work\industrial-cloud-data-portfolio\dashboard-frontend
```

### Step 2: Install Dependencies
```powershell
npm install
```

This will install:
- React 18
- TypeScript 5
- Vite 5 (build tool)
- Recharts 2 (charting library)
- Axios 1 (HTTP client)
- Tailwind CSS 3
- And all supporting libraries

**This step may take 2-5 minutes on first run.**

### Step 3: Ensure Backend is Running

In another PowerShell terminal:
```powershell
cd d:\work\industrial-cloud-data-portfolio\services\dashboard-api
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

You should see:
```
Uvicorn running on http://0.0.0.0:8080
```

### Step 4: Start Development Server

In the dashboard-frontend directory:
```powershell
npm run dev
```

You should see:
```
VITE v5.0.0  ready in xxx ms

➜  Local:   http://localhost:5173/
```

### Step 5: Open in Browser

Open your browser and go to: **http://localhost:5173**

You should see the Industrial Cloud Dashboard with 5 tabs:
- 📊 Overview
- 🖥️ Servers
- ⚙️ Services
- 📦 Containers
- 📈 Analytics

---

## Troubleshooting

### Error: "npm not found" or "npm: The term 'npm' is not recognized"

**Solution**: Node.js is not installed or PATH is not set correctly
1. Install Node.js from https://nodejs.org/
2. Make sure to check "Add to PATH" during installation
3. Restart your PowerShell window

### Error: "Connection refused" when loading dashboard

**Solution**: Backend is not running
1. Make sure the dashboard-api backend is running on port 8080
2. Check in another terminal:
   ```powershell
   cd services/dashboard-api
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080
   ```

### Error: "Port 5173 already in use"

**Solution**: Another application is using the port
1. Find and stop the process using port 5173
2. Or use a different port:
   ```powershell
   npm run dev -- --port 3000
   ```
   Then open: http://localhost:3000

### Error: CORS errors in console

**Solution**: This is expected in development. The backend CORS is configured for development.
Check that the backend is running and accessible:
```powershell
curl http://localhost:8080/api/servers/health
```

### Dashboard shows but no data loads

**Troubleshooting**:
1. Open browser DevTools (F12)
2. Go to Console tab
3. Check for error messages
4. Verify backend is running on port 8080
5. Check Network tab to see API calls
6. Make sure PostgreSQL database is accessible from backend

---

## Available Commands

After installation, you can use these commands:

```powershell
# Start development server (with auto-reload)
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Install dependencies
npm install

# Update dependencies
npm update
```

---

## Project Structure

```
dashboard-frontend/
├── src/
│   ├── components/              # React components
│   │   ├── Common.tsx           # Reusable UI components
│   │   ├── OverviewDashboard.tsx
│   │   ├── ServersDashboard.tsx
│   │   ├── ServicesDashboard.tsx
│   │   ├── ContainersDashboard.tsx
│   │   └── AnalyticsDashboard.tsx
│   ├── services/
│   │   └── api.ts               # API wrapper
│   ├── types/
│   │   └── api.ts               # TypeScript types
│   ├── App.tsx                  # Main app
│   ├── main.tsx                 # Entry point
│   └── index.css                # Styles
│
├── index.html                   # HTML template
├── vite.config.ts               # Vite config
├── tsconfig.json                # TypeScript config
├── tailwind.config.js           # Tailwind config
├── package.json                 # Dependencies
└── README.md                    # Documentation
```

---

## Backend Connection

The frontend is configured to connect to the backend API:

- **Frontend URL**: http://localhost:5173
- **Backend URL**: http://localhost:8080
- **API Calls**: Proxied automatically via Vite config

### Ensuring Backend is Ready

Before starting the frontend, verify the backend is running:

```powershell
# Test the backend API
curl http://localhost:8080/api/servers/health

# Should return JSON data like:
# {"cpu_percent": 45.2, "memory_percent": 62.1, ...}
```

---

## Next Steps

1. ✅ Install Node.js (from nodejs.org)
2. ✅ Run `npm install` in dashboard-frontend folder
3. ✅ Start backend on port 8080
4. ✅ Run `npm run dev`
5. ✅ Open http://localhost:5173 in browser
6. ✅ Explore the 5 dashboard views
7. ✅ Watch real-time data updates

---

## Production Deployment

When ready to deploy, build the production bundle:

```powershell
npm run build
```

This creates a `dist/` folder with optimized files ready for deployment to:
- Docker
- Vercel
- Netlify
- AWS S3
- Google Cloud Storage
- Any web server (Nginx, Apache, etc.)

See **FRONTEND_SETUP.md** in the parent directory for detailed deployment options.

---

## Getting Help

- **React Documentation**: https://react.dev/
- **Vite Guide**: https://vitejs.dev/
- **TypeScript**: https://www.typescriptlang.org/
- **Tailwind CSS**: https://tailwindcss.com/
- **Recharts**: https://recharts.org/

---

**Status**: Ready to set up
**Next Action**: Install Node.js, then run `npm install` && `npm run dev`
