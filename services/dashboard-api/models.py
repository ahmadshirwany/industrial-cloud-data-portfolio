"""
SQLAlchemy Models
Database models for telemetry data
"""

from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, Float
from database import Base


class ServerMetrics(Base):
    __tablename__ = "server_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP, nullable=False, index=True)
    server_id = Column(String(50), nullable=False, index=True)
    region = Column(String(50))
    environment = Column(String(50), index=True)
    cpu_percent = Column(DECIMAL(5, 2))
    memory_percent = Column(DECIMAL(5, 2))
    memory_used_gb = Column(DECIMAL(10, 2))
    memory_total_gb = Column(Integer)
    disk_used_gb = Column(Integer)
    disk_total_gb = Column(Integer)
    disk_utilization = Column(DECIMAL(5, 2))
    status = Column(String(20))
    ingested_at = Column(TIMESTAMP)


class ContainerMetrics(Base):
    __tablename__ = "container_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP, nullable=False, index=True)
    container_id = Column(String(50), nullable=False, index=True)
    service_name = Column(String(100), index=True)
    version = Column(String(50))
    environment = Column(String(50))
    cpu_percent = Column(DECIMAL(5, 2))
    memory_mb = Column(Integer)
    memory_limit_mb = Column(Integer)
    memory_utilization = Column(DECIMAL(5, 2))
    requests_per_sec = Column(Integer)
    response_time_ms = Column(DECIMAL(10, 2))
    error_count = Column(Integer)
    restart_count = Column(Integer)
    health = Column(String(20))
    ingested_at = Column(TIMESTAMP)


class ServiceMetrics(Base):
    __tablename__ = "service_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP, nullable=False, index=True)
    service_name = Column(String(100), nullable=False, index=True)
    version = Column(String(50))
    environment = Column(String(50), index=True)
    region = Column(String(50))
    total_requests = Column(Integer)
    failed_requests = Column(Integer)
    success_rate = Column(DECIMAL(5, 2))
    error_rate_percent = Column(DECIMAL(5, 2))
    avg_response_time_ms = Column(DECIMAL(10, 2))
    p95_response_time_ms = Column(DECIMAL(10, 2))
    instances_running = Column(Integer)
    cpu_avg_percent = Column(DECIMAL(5, 2))
    memory_avg_percent = Column(DECIMAL(5, 2))
    ingested_at = Column(TIMESTAMP)
