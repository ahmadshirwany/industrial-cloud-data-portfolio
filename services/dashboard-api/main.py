"""
Dashboard API Microservice - Main Application
FastAPI backend with WebSocket support for real-time telemetry dashboard
Version: 1.0.1
"""

import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Direct imports from current package
from routers import servers, containers, services, websocket, analytics
from database import engine, Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Industrial Cloud Telemetry Dashboard API",
    description="Real-time telemetry data API with WebSocket support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(servers.router, prefix="/api/servers", tags=["Servers"])
app.include_router(containers.router, prefix="/api/containers", tags=["Containers"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    logger.info("=" * 70)
    logger.info("🚀 Dashboard API Microservice Starting")
    logger.info(f"📊 Database: {os.getenv('DB_HOST', 'localhost')}")
    logger.info(f"🔗 WebSocket: Enabled")
    logger.info("=" * 70)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Industrial Cloud Telemetry Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "servers": "/api/servers",
            "containers": "/api/containers",
            "services": "/api/services",
            "analytics": "/api/analytics",
            "websocket": "/ws/metrics"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "dashboard-api"
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8080))
    # For module execution, we need to use the app object directly
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
