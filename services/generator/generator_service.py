"""
Telemetry Data Generator Microservice
Publishes metrics to GCP Pub/Sub - Streaming & Event-Driven
"""

import json
import random
from datetime import datetime


class TelemetryGeneratorService:
    """Generate telemetry data and publish to GCP Pub/Sub"""
    
    def __init__(self, pubsub):
        self.pubsub = pubsub
        
        # Configuration - Optimized for database preservation
        self.services = ["API", "DB", "Cache"]  # Reduced from 4 to 3
        self.regions = ["us-east-1"]  # Single region (consolidated)
        self.environments = ["production"]  # Only production (staging less critical)
        self.servers = [f"server-{i:02d}" for i in range(1, 11)]  # 10 servers for better visualization
        self.containers = [f"container-{i:02d}" for i in range(1, 21)]  # 20 unique containers for variety
        self.service_versions = ["v2.0.0"]  # Single version
        
        self.generated_count = 0
    
    def generate_server_metric(self) -> dict:
        """Generate a single server metric"""
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "server_id": random.choice(self.servers),
            "region": random.choice(self.regions),
            "environment": random.choice(self.environments),
            "cpu_percent": round(random.uniform(5, 95), 2),
            "memory_percent": round(random.uniform(10, 90), 2),
            "memory_used_gb": round(random.uniform(2, 15), 2),
            "memory_total_gb": 16,
            "disk_used_gb": random.randint(50, 450),
            "disk_total_gb": 500,
            "status": random.choice(["healthy", "warning", "critical"])
        }
    
    def generate_container_metric(self) -> dict:
        """Generate a single container metric"""
        # Choose memory limit first
        memory_limit_mb = random.choice([512, 1024, 2048])
        # Memory used should not exceed the limit
        memory_mb = random.randint(50, int(memory_limit_mb * 0.9))
        
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "container_id": random.choice(self.containers),
            "service_name": random.choice(self.services),
            "version": random.choice(self.service_versions),
            "environment": random.choice(self.environments),
            "cpu_percent": round(random.uniform(5, 90), 2),
            "memory_mb": memory_mb,
            "memory_limit_mb": memory_limit_mb,
            "requests_per_sec": random.randint(10, 500),
            "response_time_ms": round(random.uniform(50, 2000), 2),
            "error_count": random.randint(0, 20),
            "restart_count": random.randint(0, 3),
            "health": random.choice(["healthy", "degraded", "unhealthy"])
        }
    
    def generate_service_metric(self) -> dict:
        """Generate a single service metric"""
        total_requests = random.randint(1000, 10000)
        failed_requests = random.randint(0, int(total_requests * 0.1))
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service_name": random.choice(self.services),
            "version": random.choice(self.service_versions),
            "environment": random.choice(self.environments),
            "region": random.choice(self.regions),
            "total_requests": total_requests,
            "failed_requests": failed_requests,
            "error_rate_percent": round(random.uniform(0, 8), 2),
            "avg_response_time_ms": round(random.uniform(50, 800), 2),
            "p95_response_time_ms": round(random.uniform(200, 2000), 2),
            "instances_running": random.randint(2, 8),
            "cpu_avg_percent": round(random.uniform(20, 85), 2),
            "memory_avg_percent": round(random.uniform(30, 80), 2)
        }
    
    def generate_and_publish(self):
        """Generate metrics and publish to GCP Pub/Sub"""
        server_metric = self.generate_server_metric()
        container_metric = self.generate_container_metric()
        service_metric = self.generate_service_metric()
        
        # Publish to GCP Pub/Sub topics
        self.pubsub.publish("server_metrics", server_metric)
        self.pubsub.publish("container_metrics", container_metric)
        self.pubsub.publish("service_metrics", service_metric)
        
        self.generated_count += 3
        
        return {
            "server": server_metric,
            "container": container_metric,
            "service": service_metric
        }
    
    def get_stats(self) -> dict:
        """Get generation statistics"""
        return {
            "total_generated": self.generated_count
        }
