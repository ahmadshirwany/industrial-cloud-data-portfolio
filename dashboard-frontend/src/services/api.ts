import axios from 'axios'
import {
  ServerMetric,
  ContainerMetric,
  ServiceMetric,
  SystemHealth,
  DailyStats
} from '../types/api'

// Use absolute URL to API in Docker container
// In Docker: dashboard-api is at http://dashboard-api:8080
// In local dev: http://localhost:8080
const API_BASE = process.env.NODE_ENV === 'production' 
  ? 'http://dashboard-api:8080/api'
  : 'http://localhost:8080/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000
})

export const apiService = {
  // Server endpoints
  getServerHealth: (minutes: number = 5) =>
    api.get<any>('/servers/health', { params: { minutes } }),

  getCurrentServers: (limit: number = 50) =>
    api.get<ServerMetric[]>('/servers/current', { params: { limit } }),

  getCPUTrends: (hours: number = 24, interval: string = '5min') =>
    api.get<any[]>('/servers/trends/cpu', { params: { hours, interval } }),

  getServersByRegion: () =>
    api.get<any[]>('/servers/by-region'),

  getTopCPUServers: (limit: number = 10) =>
    api.get<any[]>('/servers/top-cpu', { params: { limit } }),

  getDiskUsage: () =>
    api.get<any[]>('/servers/disk-usage'),

  // Container endpoints
  getContainerHealth: (minutes: number = 5) =>
    api.get<any>('/containers/health', { params: { minutes } }),

  getCurrentContainers: (limit: number = 50) =>
    api.get<ContainerMetric[]>('/containers/current', { params: { limit } }),

  getContainersByService: () =>
    api.get<any[]>('/containers/by-service'),

  getHighMemoryContainers: (threshold: number = 80, limit: number = 20) =>
    api.get<any[]>('/containers/high-memory', { params: { threshold, limit } }),

  getContainerRestarts: (hours: number = 24) =>
    api.get<any[]>('/containers/restarts', { params: { hours } }),

  getThroughputTrend: (hours: number = 24) =>
    api.get<any[]>('/containers/throughput-trend', { params: { hours } }),

  // Service endpoints
  getServicePerformance: (hours: number = 1) =>
    api.get<ServiceMetric[]>('/services/performance', { params: { hours } }),

  getLatencyTrend: (hours: number = 24) =>
    api.get<any[]>('/services/latency-trend', { params: { hours } }),

  getErrorRateTrend: (hours: number = 24) =>
    api.get<any[]>('/services/error-rate-trend', { params: { hours } }),

  getSuccessRateGauge: (minutes: number = 5) =>
    api.get<any[]>('/services/success-rate-gauge', { params: { minutes } }),

  getFailedRequests: (hours: number = 24) =>
    api.get<any[]>('/services/failed-requests', { params: { hours } }),

  getServiceInstances: () =>
    api.get<any[]>('/services/instances'),

  getServicesByRegion: () =>
    api.get<any[]>('/services/by-region'),

  getSlowestServices: (limit: number = 10) =>
    api.get<any[]>('/services/slowest', { params: { limit } }),

  // Analytics endpoints
  getSystemHealth: (minutes: number = 5) =>
    api.get<SystemHealth>('/analytics/system-health', { params: { minutes } }),

  getTopCPUResources: (limit: number = 10) =>
    api.get<any[]>('/analytics/top-cpu-resources', { params: { limit } }),

  getTopMemoryResources: (limit: number = 10) =>
    api.get<any[]>('/analytics/top-memory-resources', { params: { limit } }),

  getAnomalies: (hours: number = 1) =>
    api.get<any[]>('/analytics/anomalies', { params: { hours } }),

  getDailyStats: () =>
    api.get<DailyStats>('/analytics/daily-stats'),

  getCapacityForecast: (days: number = 7) =>
    api.get<any[]>('/analytics/capacity-forecast', { params: { days } }),

  getRegionalSummary: () =>
    api.get<any[]>('/analytics/regional-summary')
}

export default api
