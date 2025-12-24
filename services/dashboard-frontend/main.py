import os
import httpx
import sys
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Initialize FastAPI app
app = FastAPI(title="Industrial Cloud Dashboard Frontend")

# Mount static files (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="services/dashboard-frontend/static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="services/dashboard-frontend/templates")

# Backend API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://dashboard-api:8080")

# Helper function to fetch from backend API
async def fetch_api(endpoint: str) -> dict:
    """Fetch data from the backend API"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"{API_BASE_URL}{endpoint}"
            print(f"ERROR: Fetching from {url}", file=sys.stderr, flush=True)
            response = await client.get(url)
            print(f"ERROR: Response status: {response.status_code}", file=sys.stderr, flush=True)
            response.raise_for_status()
            data = response.json()
            print(f"ERROR: Response data type: {type(data)}, length: {len(data) if isinstance(data, list) else 'dict'}", file=sys.stderr, flush=True)
            return data
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}", file=sys.stderr, flush=True)
        return {}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("index.html", {"request": request, "api_base_url": API_BASE_URL})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    try:
        # Fetch system health and daily stats
        health = await fetch_api("/api/analytics/system-health?minutes=5")
        stats = await fetch_api("/api/analytics/daily-stats")
        servers = await fetch_api("/api/servers/health?minutes=5")
        containers = await fetch_api("/api/containers/health?minutes=5")
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "health": health,
                "stats": stats,
                "servers": servers,
                "containers": containers,
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Interactive CV/Profile page"""
    try:
        return templates.TemplateResponse(
            "profile.html",
            {"request": request}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )

@app.get("/servers", response_class=HTMLResponse)
async def servers_page(request: Request):
    """Servers monitoring page"""
    try:
        servers = await fetch_api("/api/servers/current?limit=10")
        health = await fetch_api("/api/servers/health?minutes=5")
        
        return templates.TemplateResponse(
            "servers.html",
            {
                "request": request,
                "servers": servers,
                "health": health,
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )


@app.get("/containers", response_class=HTMLResponse)
async def containers_page(request: Request):
    """Containers monitoring page"""
    try:
        containers = await fetch_api("/api/containers/current?limit=10")
        health = await fetch_api("/api/containers/health?minutes=5")
        
        return templates.TemplateResponse(
            "containers.html",
            {
                "request": request,
                "containers": containers,
                "health": health,
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )


@app.get("/services", response_class=HTMLResponse)
async def services_page(request: Request):
    """Services monitoring page"""
    try:
        services = await fetch_api("/api/services/performance?hours=1")
        instances = await fetch_api("/api/services/instances")
        
        return templates.TemplateResponse(
            "services.html",
            {
                "request": request,
                "services": services,
                "instances": instances,
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )


@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics and insights page"""
    try:
        anomalies = await fetch_api("/api/analytics/anomalies?hours=1")
        forecast = await fetch_api("/api/analytics/capacity-forecast?days=7")
        regional = await fetch_api("/api/analytics/regional-summary")
        
        return templates.TemplateResponse(
            "analytics.html",
            {
                "request": request,
                "anomalies": anomalies,
                "forecast": forecast,
                "regional": regional,
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )


# Proxy API endpoints for Chart.js (frontend JavaScript)
@app.get("/api/cpu-trends")
async def cpu_trends(hours: int = 6):
    """Proxy endpoint for CPU trends data"""
    return await fetch_api(f"/api/analytics/cpu-trends?hours={hours}")


@app.get("/api/memory-trends")
async def memory_trends(hours: int = 6):
    """Proxy endpoint for memory trends data"""
    return await fetch_api(f"/api/analytics/memory-trends?hours={hours}")


@app.get("/api/disk-trends")
async def disk_trends(hours: int = 6):
    """Proxy endpoint for disk trends data"""
    return await fetch_api(f"/api/analytics/disk-trends?hours={hours}")


@app.get("/api/service-trends")
async def service_trends(hours: int = 6):
    """Proxy endpoint for service trends data"""
    return await fetch_api(f"/api/analytics/service-trends?hours={hours}")


# HTMX endpoints for dynamic updates
@app.get("/api/health-card", response_class=HTMLResponse)
async def health_card(request: Request):
    """HTMX endpoint for health card updates"""
    health = await fetch_api("/api/analytics/system-health?minutes=5")
    return templates.TemplateResponse(
        "components/health_card.html",
        {"request": request, "health": health}
    )


@app.get("/api/servers-table", response_class=HTMLResponse)
async def servers_table(request: Request):
    """HTMX endpoint for servers table updates"""
    response = await fetch_api("/api/servers/current?limit=10")
    
    # Handle both list and dict responses
    if isinstance(response, dict) and 'value' in response:
        servers = response['value']
    elif isinstance(response, list):
        servers = response
    else:
        servers = []
    
    # Add uptime calculation
    now = datetime.now(timezone.utc)
    
    for server in servers:
        try:
            # Parse ISO8601 timestamp
            ts_str = server.get('timestamp', '')
            if ts_str:
                # Handle timestamps with or without Z suffix and timezone info
                if 'Z' in ts_str or '+' in ts_str:
                    ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                else:
                    # Assume UTC if no timezone info
                    ts = datetime.fromisoformat(ts_str).replace(tzinfo=timezone.utc)
                
                uptime_seconds = (now - ts).total_seconds()
                uptime_hours = uptime_seconds / 3600
                
                # Format as hours or days
                if uptime_hours >= 24:
                    uptime_days = uptime_hours / 24
                    server['uptime_days'] = f"{round(uptime_days, 1)} days"
                else:
                    server['uptime_days'] = f"{round(uptime_hours, 1)} hrs"
            else:
                server['uptime_days'] = 'N/A'
        except Exception as e:
            server['uptime_days'] = f'Error: {str(e)[:20]}'
    
    return templates.TemplateResponse(
        "components/servers_table.html",
        {"request": request, "servers": servers, "now": now}
    )


@app.get("/api/containers-table", response_class=HTMLResponse)
async def containers_table(request: Request):
    """HTMX endpoint for containers table updates"""
    containers = await fetch_api("/api/containers/current?limit=10")
    return templates.TemplateResponse(
        "components/containers_table.html",
        {"request": request, "containers": containers}
    )


# Proxy endpoints for chart data
@app.get("/api/cpu-trends")
async def cpu_trends(hours: int = 6):
    """Proxy endpoint for CPU trend data"""
    return await fetch_api(f"/api/analytics/cpu-trends?hours={hours}")


@app.get("/api/memory-trends")
async def memory_trends(hours: int = 6):
    """Proxy endpoint for memory trend data"""
    return await fetch_api(f"/api/analytics/memory-trends?hours={hours}")


@app.get("/api/disk-trends")
async def disk_trends(hours: int = 6):
    """Proxy endpoint for disk trend data"""
    return await fetch_api(f"/api/analytics/disk-trends?hours={hours}")


@app.get("/api/service-trends")
async def service_trends(hours: int = 6):
    """Proxy endpoint for service trend data"""
    return await fetch_api(f"/api/analytics/service-trends?hours={hours}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "dashboard-frontend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
