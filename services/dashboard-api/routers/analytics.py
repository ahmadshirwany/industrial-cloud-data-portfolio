"""
Analytics & Aggregation Endpoints
Cross-metric analytics and system health scoring
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from services.dashboard_api.database import get_db
from services.dashboard_api.schemas import (
    SystemHealthScore,
    TopResource,
    AnomalyAlert,
    DailyStats
)

router = APIRouter()


@router.get("/system-health", response_model=SystemHealthScore)
async def get_system_health(
    minutes: int = Query(default=5, description="Time window in minutes"),
    db: Session = Depends(get_db)
):
    """
    Calculate overall system health score (0-100)
    """
    # Get server health metrics
    server_query = text("""
        SELECT 
            AVG(cpu_percent) as avg_cpu,
            AVG(memory_percent) as avg_memory,
            AVG(disk_utilization) as avg_disk,
            COUNT(CASE WHEN status = 'critical' THEN 1 END) as critical_servers
        FROM server_metrics
        WHERE timestamp > NOW() - INTERVAL '1 minute' * :minutes
    """)
    
    server_result = db.execute(server_query, {"minutes": minutes}).fetchone()
    
    # Get service health metrics
    service_query = text("""
        SELECT 
            AVG(success_rate) as avg_success_rate,
            AVG(error_rate_percent) as avg_error_rate
        FROM service_metrics
        WHERE timestamp > NOW() - INTERVAL '1 minute' * :minutes
    """)
    
    service_result = db.execute(service_query, {"minutes": minutes}).fetchone()
    
    # Calculate health score (100 = perfect)
    cpu_score = max(0, 100 - (server_result[0] or 0))
    memory_score = max(0, 100 - (server_result[1] or 0))
    disk_score = max(0, 100 - (server_result[2] or 0))
    service_score = (service_result[0] or 100)
    critical_penalty = (server_result[3] or 0) * 10
    
    overall_score = max(0, (cpu_score + memory_score + disk_score + service_score) / 4 - critical_penalty)
    
    return SystemHealthScore(
        score=round(overall_score, 2),
        avg_cpu=float(server_result[0] or 0),
        avg_memory=float(server_result[1] or 0),
        avg_disk=float(server_result[2] or 0),
        avg_success_rate=float(service_result[0] or 100),
        critical_servers=server_result[3] or 0
    )


@router.get("/top-cpu-resources", response_model=List[TopResource])
async def get_top_cpu_resources(
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    """
    Get top CPU consumers across servers
    """
    query = text("""
        WITH latest AS (
            SELECT server_id, MAX(timestamp) as max_time
            FROM server_metrics
            WHERE timestamp > NOW() - INTERVAL '5 minutes'
            GROUP BY server_id
        )
        SELECT 
            s.server_id as resource_name,
            'server' as resource_type,
            s.cpu_percent as value,
            s.region,
            s.status
        FROM server_metrics s
        INNER JOIN latest l ON s.server_id = l.server_id AND s.timestamp = l.max_time
        ORDER BY s.cpu_percent DESC
        LIMIT :limit
    """)
    
    results = db.execute(query, {"limit": limit}).fetchall()
    
    return [
        TopResource(
            resource_name=row[0],
            resource_type=row[1],
            value=float(row[2]) if row[2] else 0,
            region=row[3],
            status=row[4]
        )
        for row in results
    ]


@router.get("/top-memory-resources", response_model=List[TopResource])
async def get_top_memory_resources(
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    """
    Get top memory consumers (servers + containers)
    """
    query = text("""
        WITH server_memory AS (
            SELECT server_id, MAX(timestamp) as max_time
            FROM server_metrics
            WHERE timestamp > NOW() - INTERVAL '5 minutes'
            GROUP BY server_id
        ),
        container_memory AS (
            SELECT container_id, MAX(timestamp) as max_time
            FROM container_metrics
            WHERE timestamp > NOW() - INTERVAL '5 minutes'
            GROUP BY container_id
        ),
        servers AS (
            SELECT 
                s.server_id as resource_name,
                'server' as resource_type,
                s.memory_percent as value,
                s.region,
                s.status
            FROM server_metrics s
            INNER JOIN server_memory sm ON s.server_id = sm.server_id AND s.timestamp = sm.max_time
        ),
        containers AS (
            SELECT 
                c.container_id as resource_name,
                'container' as resource_type,
                c.memory_utilization as value,
                '' as region,
                c.health as status
            FROM container_metrics c
            INNER JOIN container_memory cm ON c.container_id = cm.container_id AND c.timestamp = cm.max_time
        )
        SELECT * FROM servers
        UNION ALL
        SELECT * FROM containers
        ORDER BY value DESC
        LIMIT :limit
    """)
    
    results = db.execute(query, {"limit": limit}).fetchall()
    
    return [
        TopResource(
            resource_name=row[0],
            resource_type=row[1],
            value=float(row[2]) if row[2] else 0,
            region=row[3] or "N/A",
            status=row[4]
        )
        for row in results
    ]


@router.get("/anomalies", response_model=List[AnomalyAlert])
async def detect_anomalies(
    hours: int = Query(default=1, description="Hours to look back"),
    db: Session = Depends(get_db)
):
    """
    Detect anomalies: CPU spikes, memory pressure, high errors
    """
    anomalies = []
    
    # CPU spike detection
    cpu_query = text("""
        SELECT 
            server_id,
            'cpu_spike' as anomaly_type,
            cpu_percent as value,
            timestamp,
            'high' as severity
        FROM server_metrics
        WHERE timestamp > NOW() - INTERVAL :hours HOUR
        AND cpu_percent > 90
        ORDER BY cpu_percent DESC
        LIMIT 20
    """)
    
    cpu_results = db.execute(cpu_query, {"hours": f"{hours} hours"}).fetchall()
    
    for row in cpu_results:
        anomalies.append(AnomalyAlert(
            resource_name=row[0],
            anomaly_type=row[1],
            value=float(row[2]) if row[2] else 0,
            timestamp=row[3],
            severity=row[4]
        ))
    
    # Memory pressure detection
    memory_query = text("""
        SELECT 
            server_id,
            'memory_pressure' as anomaly_type,
            memory_percent as value,
            timestamp,
            'high' as severity
        FROM server_metrics
        WHERE timestamp > NOW() - INTERVAL :hours HOUR
        AND memory_percent > 85
        ORDER BY memory_percent DESC
        LIMIT 20
    """)
    
    memory_results = db.execute(memory_query, {"hours": f"{hours} hours"}).fetchall()
    
    for row in memory_results:
        anomalies.append(AnomalyAlert(
            resource_name=row[0],
            anomaly_type=row[1],
            value=float(row[2]) if row[2] else 0,
            timestamp=row[3],
            severity=row[4]
        ))
    
    # Service error spike detection
    error_query = text("""
        SELECT 
            service_name,
            'error_spike' as anomaly_type,
            error_rate_percent as value,
            timestamp,
            'critical' as severity
        FROM service_metrics
        WHERE timestamp > NOW() - INTERVAL :hours HOUR
        AND error_rate_percent > 10
        ORDER BY error_rate_percent DESC
        LIMIT 20
    """)
    
    error_results = db.execute(error_query, {"hours": f"{hours} hours"}).fetchall()
    
    for row in error_results:
        anomalies.append(AnomalyAlert(
            resource_name=row[0],
            anomaly_type=row[1],
            value=float(row[2]) if row[2] else 0,
            timestamp=row[3],
            severity=row[4]
        ))
    
    # Sort by timestamp descending
    anomalies.sort(key=lambda x: x.timestamp, reverse=True)
    
    return anomalies[:50]


@router.get("/daily-stats", response_model=DailyStats)
async def get_daily_stats(
    db: Session = Depends(get_db)
):
    """
    Get daily aggregated statistics
    """
    # Server stats
    server_query = text("""
        SELECT 
            AVG(cpu_percent) as avg_cpu,
            AVG(memory_percent) as avg_memory,
            AVG(disk_utilization) as avg_disk,
            COUNT(DISTINCT server_id) as total_servers
        FROM server_metrics
        WHERE timestamp > NOW() - INTERVAL '24 hours'
    """)
    
    server_result = db.execute(server_query).fetchone()
    
    # Service stats
    service_query = text("""
        SELECT 
            SUM(total_requests) as total_requests,
            SUM(failed_requests) as failed_requests,
            AVG(success_rate) as avg_success_rate
        FROM service_metrics
        WHERE timestamp > NOW() - INTERVAL '24 hours'
    """)
    
    service_result = db.execute(service_query).fetchone()
    
    # Container stats
    container_query = text("""
        SELECT 
            SUM(restart_count) as total_restarts,
            COUNT(DISTINCT container_id) as active_containers
        FROM container_metrics
        WHERE timestamp > NOW() - INTERVAL '24 hours'
    """)
    
    container_result = db.execute(container_query).fetchone()
    
    return DailyStats(
        avg_cpu=float(server_result[0] or 0),
        avg_memory=float(server_result[1] or 0),
        avg_disk=float(server_result[2] or 0),
        total_servers=server_result[3] or 0,
        total_requests=service_result[0] or 0,
        failed_requests=service_result[1] or 0,
        avg_success_rate=float(service_result[2] or 100),
        total_restarts=container_result[0] or 0,
        active_containers=container_result[1] or 0
    )


@router.get("/capacity-forecast")
async def get_capacity_forecast(
    days: int = Query(default=7, le=30),
    db: Session = Depends(get_db)
):
    """
    Forecast resource capacity based on historical growth
    """
    query = text("""
        WITH daily_avg AS (
            SELECT 
                DATE(timestamp) as date,
                AVG(cpu_percent) as avg_cpu,
                AVG(memory_percent) as avg_memory,
                AVG(disk_utilization) as avg_disk
            FROM server_metrics
            WHERE timestamp > NOW() - INTERVAL :days DAY
            GROUP BY DATE(timestamp)
            ORDER BY date
        )
        SELECT 
            date,
            avg_cpu,
            avg_memory,
            avg_disk
        FROM daily_avg
    """)
    
    results = db.execute(query, {"days": f"{days} days"}).fetchall()
    
    return [
        {
            "date": row[0],
            "avg_cpu": float(row[1]) if row[1] else 0,
            "avg_memory": float(row[2]) if row[2] else 0,
            "avg_disk": float(row[3]) if row[3] else 0
        }
        for row in results
    ]


@router.get("/regional-summary")
async def get_regional_summary(
    db: Session = Depends(get_db)
):
    """
    Get summary metrics by region
    """
    query = text("""
        SELECT 
            region,
            COUNT(DISTINCT server_id) as server_count,
            AVG(cpu_percent) as avg_cpu,
            AVG(memory_percent) as avg_memory,
            AVG(disk_utilization) as avg_disk,
            COUNT(CASE WHEN status = 'critical' THEN 1 END) as critical_count
        FROM server_metrics
        WHERE timestamp > NOW() - INTERVAL '5 minutes'
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
            "avg_disk": float(row[4]) if row[4] else 0,
            "critical_count": row[5] or 0
        }
        for row in results
    ]
