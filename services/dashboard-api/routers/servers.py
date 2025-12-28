"""
Server Metrics Endpoints
APIs for server telemetry data
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from schemas import (
    ServerMetricBase,
    ServerHealthSummary,
    ServerTrend
)

router = APIRouter()


@router.get("/health", response_model=ServerHealthSummary)
async def get_server_health(
    minutes: int = Query(default=30, description="Time window in minutes"),
    db: Session = Depends(get_db)
):
    """
    Get current server health summary
    Returns counts by status and average resource usage
    """
    query = text(f"""
        WITH latest_servers AS (
            SELECT DISTINCT ON (server_id)
                server_id,
                status,
                cpu_percent,
                memory_percent,
                disk_utilization,
                timestamp
            FROM server_metrics
            WHERE timestamp > NOW() - INTERVAL '{minutes} minutes'
            ORDER BY server_id, timestamp DESC
        )
        SELECT 
            COUNT(server_id) as total_servers,
            COUNT(CASE WHEN status = 'healthy' THEN 1 END) as healthy_servers,
            COUNT(CASE WHEN status = 'warning' THEN 1 END) as warning_servers,
            COUNT(CASE WHEN status = 'critical' THEN 1 END) as critical_servers,
            AVG(cpu_percent) as avg_cpu,
            AVG(memory_percent) as avg_memory,
            AVG(disk_utilization) as avg_disk
        FROM latest_servers
    """)
    
    result = db.execute(query).fetchone()
    
    return ServerHealthSummary(
        total_servers=int(result[0] or 0),
        healthy_servers=int(result[1] or 0),
        warning_servers=int(result[2] or 0),
        critical_servers=int(result[3] or 0),
        avg_cpu=round(float(result[4] or 0), 2),
        avg_memory=round(float(result[5] or 0), 2),
        avg_disk=round(float(result[6] or 0), 2)
    )


@router.get("/current", response_model=List[ServerMetricBase])
async def get_current_servers(
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db)
):
    """
    Get current state of all servers (most recent metrics)
    """
    query = text("""
        SELECT DISTINCT ON (s.server_id)
            s.timestamp,
            s.server_id,
            s.region,
            s.environment,
            s.cpu_percent,
            s.memory_percent,
            s.disk_utilization,
            s.status
        FROM server_metrics s
        WHERE s.timestamp > NOW() - INTERVAL '30 minutes'
        ORDER BY s.server_id, s.timestamp DESC
        LIMIT :limit
    """)
    
    results = db.execute(query, {"limit": limit}).fetchall()
    
    return [
        ServerMetricBase(
            timestamp=row[0],
            server_id=row[1],
            region=row[2],
            environment=row[3],
            cpu_percent=float(row[4]) if row[4] else None,
            memory_percent=float(row[5]) if row[5] else None,
            disk_utilization=float(row[6]) if row[6] else None,
            status=row[7]
        )
        for row in results
    ]


@router.get("/trends/cpu", response_model=List[ServerTrend])
async def get_cpu_trend(
    hours: int = Query(default=24, le=168, description="Hours to look back"),
    interval: str = Query(default="5min", description="Time bucket (5min, 15min, 1hour)"),
    db: Session = Depends(get_db)
):
    """
    Get CPU usage trends over time
    Aggregated by time intervals
    """
    interval_map = {
        "5min": "5 minutes",
        "15min": "15 minutes",
        "1hour": "1 hour"
    }
    
    trunc_interval = interval_map.get(interval, "5 minutes")
    
    query = text(f"""
        SELECT 
            DATE_TRUNC('minute', timestamp - (EXTRACT(MINUTE FROM timestamp)::int % 5) * INTERVAL '1 minute') as time,
            AVG(cpu_percent) as avg_cpu,
            AVG(memory_percent) as avg_memory,
            AVG(disk_utilization) as avg_disk
        FROM server_metrics
        WHERE timestamp > NOW() - INTERVAL '{hours} hours'
        GROUP BY time
        ORDER BY time
    """)
    
    results = db.execute(query).fetchall()
    
    return [
        ServerTrend(
            time=row[0],
            avg_cpu=float(row[1]) if row[1] else 0,
            avg_memory=float(row[2]) if row[2] else 0,
            avg_disk=float(row[3]) if row[3] else 0
        )
        for row in results
    ]


@router.get("/by-region")
async def get_servers_by_region(
    db: Session = Depends(get_db)
):
    """
    Get server metrics grouped by region
    """
    query = text("""
        SELECT 
            region,
            COUNT(DISTINCT server_id) as server_count,
            AVG(cpu_percent) as avg_cpu,
            AVG(memory_percent) as avg_memory,
            AVG(disk_utilization) as avg_disk
        FROM server_metrics
        WHERE timestamp > NOW() - INTERVAL '30 minutes'
        GROUP BY region
        ORDER BY server_count DESC
    """)
    
    results = db.execute(query).fetchall()
    
    return [
        {
            "region": row[0],
            "server_count": row[1],
            "avg_cpu": float(row[2]) if row[2] else 0,
            "avg_memory": float(row[3]) if row[3] else 0,
            "avg_disk": float(row[4]) if row[4] else 0
        }
        for row in results
    ]


@router.get("/top-cpu")
async def get_top_cpu_servers(
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    """
    Get servers with highest CPU usage
    """
    query = text("""
        WITH latest AS (
            SELECT server_id, MAX(timestamp) as max_time
            FROM server_metrics
            WHERE timestamp > NOW() - INTERVAL '30 minutes'
            GROUP BY server_id
        )
        SELECT 
            s.server_id,
            s.region,
            s.cpu_percent,
            s.status,
            s.timestamp
        FROM server_metrics s
        INNER JOIN latest l ON s.server_id = l.server_id AND s.timestamp = l.max_time
        ORDER BY s.cpu_percent DESC
        LIMIT :limit
    """)
    
    results = db.execute(query, {"limit": limit}).fetchall()
    
    return [
        {
            "server_id": row[0],
            "region": row[1],
            "cpu_percent": float(row[2]) if row[2] else 0,
            "status": row[3],
            "timestamp": row[4]
        }
        for row in results
    ]


@router.get("/disk-usage")
async def get_disk_usage(
    db: Session = Depends(get_db)
):
    """
    Get disk usage statistics across all servers
    """
    query = text("""
        WITH latest AS (
            SELECT server_id, MAX(timestamp) as max_time
            FROM server_metrics
            WHERE timestamp > NOW() - INTERVAL '30 minutes'
            GROUP BY server_id
        )
        SELECT 
            s.server_id,
            s.region,
            s.disk_used_gb,
            s.disk_total_gb,
            s.disk_utilization,
            s.timestamp
        FROM server_metrics s
        INNER JOIN latest l ON s.server_id = l.server_id AND s.timestamp = l.max_time
        WHERE s.disk_utilization > 50
        ORDER BY s.disk_utilization DESC
    """)
    
    results = db.execute(query).fetchall()
    
    return [
        {
            "server_id": row[0],
            "region": row[1],
            "disk_used_gb": row[2],
            "disk_total_gb": row[3],
            "disk_utilization": float(row[4]) if row[4] else 0,
            "timestamp": row[5]
        }
        for row in results
    ]
