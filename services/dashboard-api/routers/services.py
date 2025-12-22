"""
Service Metrics Endpoints
APIs for service-level telemetry data
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from services.dashboard_api.database import get_db
from services.dashboard_api.schemas import (
    ServicePerformance,
    ServiceLatencyTrend
)

router = APIRouter()


@router.get("/performance", response_model=List[ServicePerformance])
async def get_service_performance(
    hours: int = Query(default=1, description="Hours to look back"),
    db: Session = Depends(get_db)
):
    """
    Get performance metrics for all services
    """
    query = text("""
        SELECT 
            service_name,
            AVG(success_rate) as avg_success_rate,
            AVG(error_rate_percent) as avg_error_rate,
            AVG(avg_response_time_ms) as avg_response_time,
            AVG(p95_response_time_ms) as p95_response_time,
            SUM(total_requests) as total_requests,
            SUM(failed_requests) as failed_requests
        FROM service_metrics
        WHERE timestamp > NOW() - INTERVAL :hours HOUR
        GROUP BY service_name
        ORDER BY avg_success_rate ASC
    """)
    
    results = db.execute(query, {"hours": f"{hours} hours"}).fetchall()
    
    return [
        ServicePerformance(
            service_name=row[0],
            avg_success_rate=float(row[1]) if row[1] else 0,
            avg_error_rate=float(row[2]) if row[2] else 0,
            avg_response_time=float(row[3]) if row[3] else 0,
            p95_response_time=float(row[4]) if row[4] else 0,
            total_requests=row[5] or 0,
            failed_requests=row[6] or 0
        )
        for row in results
    ]


@router.get("/latency-trend", response_model=List[ServiceLatencyTrend])
async def get_latency_trend(
    hours: int = Query(default=24, le=168),
    db: Session = Depends(get_db)
):
    """
    Get latency trends for all services over time
    """
    query = text("""
        SELECT 
            DATE_TRUNC('minute', timestamp - (EXTRACT(MINUTE FROM timestamp)::int % 5) * INTERVAL '1 minute') as time,
            service_name,
            AVG(avg_response_time_ms) as avg_latency,
            AVG(p95_response_time_ms) as p95_latency
        FROM service_metrics
        WHERE timestamp > NOW() - INTERVAL :hours HOUR
        GROUP BY time, service_name
        ORDER BY time, service_name
    """)
    
    results = db.execute(query, {"hours": f"{hours} hours"}).fetchall()
    
    return [
        ServiceLatencyTrend(
            time=row[0],
            service_name=row[1],
            avg_latency=float(row[2]) if row[2] else 0,
            p95_latency=float(row[3]) if row[3] else 0
        )
        for row in results
    ]


@router.get("/error-rate-trend")
async def get_error_rate_trend(
    hours: int = Query(default=24, le=168),
    db: Session = Depends(get_db)
):
    """
    Get error rate trends over time
    """
    query = text("""
        SELECT 
            DATE_TRUNC('minute', timestamp - (EXTRACT(MINUTE FROM timestamp)::int % 5) * INTERVAL '1 minute') as time,
            service_name,
            AVG(error_rate_percent) as avg_error_rate
        FROM service_metrics
        WHERE timestamp > NOW() - INTERVAL :hours HOUR
        GROUP BY time, service_name
        ORDER BY time, service_name
    """)
    
    results = db.execute(query, {"hours": f"{hours} hours"}).fetchall()
    
    return [
        {
            "time": row[0],
            "service_name": row[1],
            "avg_error_rate": float(row[2]) if row[2] else 0
        }
        for row in results
    ]


@router.get("/success-rate-gauge")
async def get_success_rate_gauge(
    minutes: int = Query(default=5, description="Time window in minutes"),
    db: Session = Depends(get_db)
):
    """
    Get current success rate for gauge charts (0-100%)
    """
    query = text("""
        SELECT 
            service_name,
            AVG(success_rate) as success_rate,
            AVG(error_rate_percent) as error_rate
        FROM service_metrics
        WHERE timestamp > NOW() - INTERVAL :minutes MINUTE
        GROUP BY service_name
        ORDER BY success_rate ASC
    """)
    
    results = db.execute(query, {"minutes": f"{minutes} minutes"}).fetchall()
    
    return [
        {
            "service_name": row[0],
            "success_rate": float(row[1]) if row[1] else 0,
            "error_rate": float(row[2]) if row[2] else 0
        }
        for row in results
    ]


@router.get("/failed-requests")
async def get_failed_requests(
    hours: int = Query(default=24, description="Hours to look back"),
    db: Session = Depends(get_db)
):
    """
    Get total failed requests by service
    """
    query = text("""
        SELECT 
            service_name,
            SUM(failed_requests) as total_failures,
            SUM(total_requests) as total_requests,
            AVG(error_rate_percent) as avg_error_rate
        FROM service_metrics
        WHERE timestamp > NOW() - INTERVAL :hours HOUR
        GROUP BY service_name
        ORDER BY total_failures DESC
    """)
    
    results = db.execute(query, {"hours": f"{hours} hours"}).fetchall()
    
    return [
        {
            "service_name": row[0],
            "total_failures": row[1] or 0,
            "total_requests": row[2] or 0,
            "avg_error_rate": float(row[3]) if row[3] else 0
        }
        for row in results
    ]


@router.get("/instances")
async def get_service_instances(
    db: Session = Depends(get_db)
):
    """
    Get running instances count per service
    """
    query = text("""
        WITH latest AS (
            SELECT service_name, MAX(timestamp) as max_time
            FROM service_metrics
            WHERE timestamp > NOW() - INTERVAL '5 minutes'
            GROUP BY service_name
        )
        SELECT 
            s.service_name,
            s.instances_running,
            s.cpu_avg_percent,
            s.memory_avg_percent,
            s.timestamp
        FROM service_metrics s
        INNER JOIN latest l ON s.service_name = l.service_name AND s.timestamp = l.max_time
        ORDER BY s.instances_running DESC
    """)
    
    results = db.execute(query).fetchall()
    
    return [
        {
            "service_name": row[0],
            "instances_running": row[1] or 0,
            "cpu_avg_percent": float(row[2]) if row[2] else 0,
            "memory_avg_percent": float(row[3]) if row[3] else 0,
            "timestamp": row[4]
        }
        for row in results
    ]


@router.get("/by-region")
async def get_services_by_region(
    db: Session = Depends(get_db)
):
    """
    Get service performance by region
    """
    query = text("""
        SELECT 
            region,
            service_name,
            AVG(avg_response_time_ms) as avg_latency,
            AVG(success_rate) as avg_success_rate
        FROM service_metrics
        WHERE timestamp > NOW() - INTERVAL '1 hour'
        GROUP BY region, service_name
        ORDER BY region, avg_latency
    """)
    
    results = db.execute(query).fetchall()
    
    return [
        {
            "region": row[0],
            "service_name": row[1],
            "avg_latency": float(row[2]) if row[2] else 0,
            "avg_success_rate": float(row[3]) if row[3] else 0
        }
        for row in results
    ]


@router.get("/slowest")
async def get_slowest_services(
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    """
    Get services with highest latency
    """
    query = text("""
        SELECT 
            service_name,
            AVG(avg_response_time_ms) as avg_latency,
            AVG(p95_response_time_ms) as p95_latency,
            AVG(success_rate) as success_rate
        FROM service_metrics
        WHERE timestamp > NOW() - INTERVAL '1 hour'
        GROUP BY service_name
        ORDER BY avg_latency DESC
        LIMIT :limit
    """)
    
    results = db.execute(query, {"limit": limit}).fetchall()
    
    return [
        {
            "service_name": row[0],
            "avg_latency": float(row[1]) if row[1] else 0,
            "p95_latency": float(row[2]) if row[2] else 0,
            "success_rate": float(row[3]) if row[3] else 0
        }
        for row in results
    ]
