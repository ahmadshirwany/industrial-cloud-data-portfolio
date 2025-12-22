"""
Pydantic Schemas
Request/Response models for API endpoints
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# Server Schemas
class ServerMetricBase(BaseModel):
    timestamp: datetime
    server_id: str
    region: Optional[str] = None
    environment: Optional[str] = None
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    disk_utilization: Optional[float] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class ServerHealthSummary(BaseModel):
    total_servers: int
    healthy_servers: int
    warning_servers: int
    critical_servers: int
    avg_cpu: float
    avg_memory: float
    avg_disk: float


class ServerTrend(BaseModel):
    time: datetime
    avg_cpu: float
    avg_memory: float
    avg_disk: float


# Container Schemas
class ContainerMetricBase(BaseModel):
    timestamp: datetime
    container_id: str
    service_name: Optional[str] = None
    cpu_percent: Optional[float] = None
    memory_utilization: Optional[float] = None
    requests_per_sec: Optional[int] = None
    health: Optional[str] = None

    class Config:
        from_attributes = True


class ContainerHealthSummary(BaseModel):
    total_containers: int
    healthy_containers: int
    degraded_containers: int
    unhealthy_containers: int
    avg_memory_utilization: float
    total_restarts: int


# Service Schemas
class ServiceMetricBase(BaseModel):
    timestamp: datetime
    service_name: str
    success_rate: Optional[float] = None
    error_rate_percent: Optional[float] = None
    avg_response_time_ms: Optional[float] = None
    p95_response_time_ms: Optional[float] = None

    class Config:
        from_attributes = True


class ServicePerformance(BaseModel):
    service_name: str
    avg_success_rate: float
    avg_error_rate: float
    avg_response_time: float
    p95_response_time: float
    total_requests: int
    failed_requests: int


class ServiceLatencyTrend(BaseModel):
    time: datetime
    service_name: str
    avg_latency: float
    p95_latency: float


# Analytics Schemas
class SystemHealthScore(BaseModel):
    score: float
    avg_cpu: float
    avg_memory: float
    avg_disk: float
    avg_success_rate: float
    critical_servers: int


class TopResource(BaseModel):
    resource_name: str
    resource_type: str
    value: float
    region: Optional[str] = None
    status: Optional[str] = None


class AnomalyAlert(BaseModel):
    resource_name: str
    anomaly_type: str
    value: float
    timestamp: datetime
    severity: str


class DailyStats(BaseModel):
    avg_cpu: float
    avg_memory: float
    avg_disk: float
    total_servers: int
    total_requests: int
    failed_requests: int
    avg_success_rate: float
    total_restarts: int
    active_containers: int


# WebSocket Schema
class MetricsUpdate(BaseModel):
    timestamp: datetime
    servers: Optional[dict] = None
    containers: Optional[dict] = None
    services: Optional[dict] = None
