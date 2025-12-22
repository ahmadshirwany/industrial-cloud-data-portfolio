export interface ServerMetric {
  timestamp: string
  server_id: string
  region: string
  environment: string
  cpu_percent: number
  memory_percent: number
  disk_utilization: number
  status: 'healthy' | 'warning' | 'critical'
}

export interface ContainerMetric {
  timestamp: string
  container_id: string
  service_name: string
  memory_utilization: number
  requests_per_sec: number
  health: 'healthy' | 'degraded' | 'unhealthy'
  restart_count: number
}

export interface ServiceMetric {
  service_name: string
  avg_success_rate: number
  avg_error_rate: number
  avg_response_time: number
  p95_response_time: number
  total_requests: number
  failed_requests: number
}

export interface SystemHealth {
  score: number
  avg_cpu: number
  avg_memory: number
  avg_disk: number
  avg_success_rate: number
  critical_servers: number
}

export interface DailyStats {
  avg_cpu: number
  avg_memory: number
  avg_disk: number
  total_servers: number
  total_requests: number
  failed_requests: number
  avg_success_rate: number
  total_restarts: number
  active_containers: number
}

export interface WebSocketMetrics {
  timestamp: string
  servers: {
    total: number
    avg_cpu: number
    avg_memory: number
    avg_disk: number
    healthy: number
    warning: number
    critical: number
  }
  containers: {
    total: number
    avg_memory: number
    avg_rps: number
    healthy: number
    total_restarts: number
  }
  services: {
    total: number
    avg_success_rate: number
    avg_error_rate: number
    avg_latency: number
    total_requests: number
  }
}
