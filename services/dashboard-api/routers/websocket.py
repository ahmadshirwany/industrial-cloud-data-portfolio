"""
WebSocket Endpoint for Real-time Updates
Streams metrics to frontend clients
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import asyncio
import json
from datetime import datetime
from typing import List

from services.dashboard_api.database import get_db

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


@router.websocket("/metrics")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming real-time metrics
    Sends updates every 30 seconds
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Get database session
            db = next(get_db())
            
            try:
                # Fetch latest metrics
                metrics_data = await get_latest_metrics(db)
                
                # Send to client
                await websocket.send_json(metrics_data)
                
            except Exception as e:
                print(f"Error fetching metrics: {e}")
            finally:
                db.close()
            
            # Wait 30 seconds before next update
            await asyncio.sleep(30)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def get_latest_metrics(db: Session) -> dict:
    """
    Fetch latest metrics from all tables
    """
    
    # Get server metrics
    server_query = text("""
        WITH latest AS (
            SELECT server_id, MAX(timestamp) as max_time
            FROM server_metrics
            WHERE timestamp > NOW() - INTERVAL '2 minutes'
            GROUP BY server_id
        )
        SELECT 
            COUNT(*) as total_servers,
            AVG(s.cpu_percent) as avg_cpu,
            AVG(s.memory_percent) as avg_memory,
            AVG(s.disk_utilization) as avg_disk,
            COUNT(CASE WHEN s.status = 'healthy' THEN 1 END) as healthy_servers,
            COUNT(CASE WHEN s.status = 'warning' THEN 1 END) as warning_servers,
            COUNT(CASE WHEN s.status = 'critical' THEN 1 END) as critical_servers
        FROM server_metrics s
        INNER JOIN latest l ON s.server_id = l.server_id AND s.timestamp = l.max_time
    """)
    
    server_result = db.execute(server_query).fetchone()
    
    # Get container metrics
    container_query = text("""
        WITH latest AS (
            SELECT container_id, MAX(timestamp) as max_time
            FROM container_metrics
            WHERE timestamp > NOW() - INTERVAL '2 minutes'
            GROUP BY container_id
        )
        SELECT 
            COUNT(*) as total_containers,
            AVG(c.memory_utilization) as avg_memory,
            AVG(c.requests_per_sec) as avg_rps,
            COUNT(CASE WHEN c.health = 'healthy' THEN 1 END) as healthy_containers,
            SUM(c.restart_count) as total_restarts
        FROM container_metrics c
        INNER JOIN latest l ON c.container_id = l.container_id AND c.timestamp = l.max_time
    """)
    
    container_result = db.execute(container_query).fetchone()
    
    # Get service metrics
    service_query = text("""
        WITH latest AS (
            SELECT service_name, MAX(timestamp) as max_time
            FROM service_metrics
            WHERE timestamp > NOW() - INTERVAL '2 minutes'
            GROUP BY service_name
        )
        SELECT 
            COUNT(*) as total_services,
            AVG(s.success_rate) as avg_success_rate,
            AVG(s.error_rate_percent) as avg_error_rate,
            AVG(s.avg_response_time_ms) as avg_latency,
            SUM(s.total_requests) as total_requests
        FROM service_metrics s
        INNER JOIN latest l ON s.service_name = l.service_name AND s.timestamp = l.max_time
    """)
    
    service_result = db.execute(service_query).fetchone()
    
    # Build response
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "servers": {
            "total": server_result[0] or 0,
            "avg_cpu": round(float(server_result[1] or 0), 2),
            "avg_memory": round(float(server_result[2] or 0), 2),
            "avg_disk": round(float(server_result[3] or 0), 2),
            "healthy": server_result[4] or 0,
            "warning": server_result[5] or 0,
            "critical": server_result[6] or 0
        },
        "containers": {
            "total": container_result[0] or 0,
            "avg_memory": round(float(container_result[1] or 0), 2),
            "avg_rps": round(float(container_result[2] or 0), 2),
            "healthy": container_result[3] or 0,
            "total_restarts": container_result[4] or 0
        },
        "services": {
            "total": service_result[0] or 0,
            "avg_success_rate": round(float(service_result[1] or 100), 2),
            "avg_error_rate": round(float(service_result[2] or 0), 2),
            "avg_latency": round(float(service_result[3] or 0), 2),
            "total_requests": service_result[4] or 0
        }
    }


@router.get("/connections")
async def get_active_connections():
    """
    Get count of active WebSocket connections
    """
    return {
        "active_connections": len(manager.active_connections),
        "timestamp": datetime.utcnow().isoformat()
    }
