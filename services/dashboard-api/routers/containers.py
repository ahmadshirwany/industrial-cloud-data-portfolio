"""
Container Metrics Endpoints
APIs for container telemetry data
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from database import get_db
from schemas import (
    ContainerMetricBase,
    ContainerHealthSummary
)

router = APIRouter()


@router.get("/health", response_model=ContainerHealthSummary)
async def get_container_health(
    minutes: int = Query(default=30, description="Time window in minutes"),
    db: Session = Depends(get_db)
):
    """
    Get container health summary
    """
    query = text(f"""
        SELECT 
            COUNT(DISTINCT container_id) as total_containers,
            COUNT(DISTINCT CASE WHEN health = 'healthy' THEN container_id END) as healthy_containers,
            COUNT(DISTINCT CASE WHEN health = 'degraded' THEN container_id END) as degraded_containers,
            COUNT(DISTINCT CASE WHEN health = 'unhealthy' THEN container_id END) as unhealthy_containers,
            AVG(memory_utilization) as avg_memory_utilization,
            SUM(restart_count) as total_restarts
        FROM container_metrics
        WHERE timestamp > NOW() - INTERVAL '{minutes} minutes'
    """)
    
    result = db.execute(query).fetchone()
    
    return ContainerHealthSummary(
        total_containers=int(result[0] or 0),
        healthy_containers=int(result[1] or 0),
        degraded_containers=int(result[2] or 0),
        unhealthy_containers=int(result[3] or 0),
        avg_memory_utilization=round(float(result[4] or 0), 2),
        total_restarts=int(result[5] or 0)
    )


@router.get("/current", response_model=List[ContainerMetricBase])
async def get_current_containers(
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db)
):
    """
    Get current state of all containers
    """
    query = text("""
        SELECT DISTINCT ON (c.container_id)
            c.timestamp,
            c.container_id,
            c.service_name,
            c.cpu_percent,
            c.memory_utilization,
            c.requests_per_sec,
            c.health
        FROM container_metrics c
        WHERE c.timestamp > NOW() - INTERVAL '30 minutes'
        ORDER BY c.container_id, c.timestamp DESC
        LIMIT :limit
    """)
    
    results = db.execute(query, {"limit": limit}).fetchall()
    
    return [
        ContainerMetricBase(
            timestamp=row[0],
            container_id=row[1],
            service_name=row[2],
            cpu_percent=float(row[3]) if row[3] else None,
            memory_utilization=float(row[4]) if row[4] else None,
            requests_per_sec=row[5],
            health=row[6]
        )
        for row in results
    ]


@router.get("/by-service")
async def get_containers_by_service(
    db: Session = Depends(get_db)
):
    """
    Get container metrics grouped by service
    """
    query = text("""
        SELECT 
            service_name,
            COUNT(DISTINCT container_id) as container_count,
            AVG(memory_utilization) as avg_memory,
            AVG(requests_per_sec) as avg_rps,
            SUM(restart_count) as total_restarts,
            COUNT(CASE WHEN health = 'healthy' THEN 1 END) as healthy_count
        FROM container_metrics
        WHERE timestamp > NOW() - INTERVAL '30 minutes'
        GROUP BY service_name
        ORDER BY container_count DESC
    """)
    
    results = db.execute(query).fetchall()
    
    return [
        {
            "service_name": row[0],
            "container_count": row[1],
            "avg_memory": float(row[2]) if row[2] else 0,
            "avg_rps": float(row[3]) if row[3] else 0,
            "total_restarts": row[4] or 0,
            "healthy_count": row[5] or 0
        }
        for row in results
    ]


@router.get("/high-memory")
async def get_high_memory_containers(
    threshold: float = Query(default=80.0, description="Memory utilization threshold"),
    limit: int = Query(default=20, le=50),
    db: Session = Depends(get_db)
):
    """
    Get containers with high memory usage
    """
    query = text("""
        WITH latest AS (
            SELECT container_id, MAX(timestamp) as max_time
            FROM container_metrics
            WHERE timestamp > NOW() - INTERVAL '30 minutes'
            GROUP BY container_id
        )
        SELECT 
            c.container_id,
            c.service_name,
            c.memory_utilization,
            c.memory_mb,
            c.memory_limit_mb,
            c.health,
            c.timestamp
        FROM container_metrics c
        INNER JOIN latest l ON c.container_id = l.container_id AND c.timestamp = l.max_time
        WHERE c.memory_utilization > :threshold
        ORDER BY c.memory_utilization DESC
        LIMIT :limit
    """)
    
    results = db.execute(query, {"threshold": threshold, "limit": limit}).fetchall()
    
    return [
        {
            "container_id": row[0],
            "service_name": row[1],
            "memory_utilization": float(row[2]) if row[2] else 0,
            "memory_mb": row[3],
            "memory_limit_mb": row[4],
            "health": row[5],
            "timestamp": row[6]
        }
        for row in results
    ]


@router.get("/restarts")
async def get_container_restarts(
    hours: int = Query(default=24, description="Hours to look back"),
    db: Session = Depends(get_db)
):
    """
    Get containers with restart activity
    """
    query = text("""
        SELECT 
            container_id,
            service_name,
            restart_count,
            health,
            MAX(timestamp) as last_seen
        FROM container_metrics
        WHERE timestamp > NOW() - INTERVAL :hours HOUR
        AND restart_count > 0
        GROUP BY container_id, service_name, restart_count, health
        ORDER BY restart_count DESC
        LIMIT 50
    """)
    
    results = db.execute(query, {"hours": f"{hours} hours"}).fetchall()
    
    return [
        {
            "container_id": row[0],
            "service_name": row[1],
            "restart_count": row[2],
            "health": row[3],
            "last_seen": row[4]
        }
        for row in results
    ]


@router.get("/throughput-trend")
async def get_throughput_trend(
    hours: int = Query(default=24, le=168),
    db: Session = Depends(get_db)
):
    """
    Get requests per second trend over time
    """
    query = text("""
        SELECT 
            DATE_TRUNC('minute', timestamp - (EXTRACT(MINUTE FROM timestamp)::int % 5) * INTERVAL '1 minute') as time,
            AVG(requests_per_sec) as avg_rps,
            MAX(requests_per_sec) as max_rps,
            MIN(requests_per_sec) as min_rps
        FROM container_metrics
        WHERE timestamp > NOW() - INTERVAL :hours HOUR
        GROUP BY time
        ORDER BY time
    """)
    
    results = db.execute(query, {"hours": f"{hours} hours"}).fetchall()
    
    return [
        {
            "time": row[0],
            "avg_rps": float(row[1]) if row[1] else 0,
            "max_rps": float(row[2]) if row[2] else 0,
            "min_rps": float(row[3]) if row[3] else 0
        }
        for row in results
    ]
