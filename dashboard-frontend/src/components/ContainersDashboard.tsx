import React, { useEffect, useState } from 'react'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { apiService } from '../services/api'
import { StatusBadge, DataTable } from './Common'

export const ContainersDashboard: React.FC = () => {
  const [containers, setContainers] = useState<any[]>([])
  const [byService, setByService] = useState<any[]>([])
  const [throughput, setThroughput] = useState<any[]>([])
  const [restarts, setRestarts] = useState<any[]>([])
  const [health, setHealth] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [containersRes, serviceRes, throughputRes, restartsRes, healthRes] = await Promise.all([
          apiService.getCurrentContainers(30),
          apiService.getContainersByService(),
          apiService.getThroughputTrend(24),
          apiService.getContainerRestarts(24),
          apiService.getContainerHealth()
        ])

        setContainers(Array.isArray(containersRes.data) ? containersRes.data : [])
        setByService(Array.isArray(serviceRes.data) ? serviceRes.data : [])
        setThroughput(Array.isArray(throughputRes.data) ? throughputRes.data : [])
        setRestarts(Array.isArray(restartsRes.data) ? restartsRes.data : [])
        setHealth(healthRes.data || healthRes)
      } catch (err) {
        console.error('Failed to fetch container data', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 60000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <div>Loading container metrics...</div>

  return (
    <div className="space-y-6">
      {/* Container Health Summary */}
      {health && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-green-50 rounded-lg p-4 border border-green-200">
            <p className="text-xs text-gray-600 mb-2">Healthy</p>
            <p className="text-3xl font-bold text-green-600">{health.healthy_containers}</p>
          </div>
          <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
            <p className="text-xs text-gray-600 mb-2">Degraded</p>
            <p className="text-3xl font-bold text-orange-600">{health.degraded_containers}</p>
          </div>
          <div className="bg-red-50 rounded-lg p-4 border border-red-200">
            <p className="text-xs text-gray-600 mb-2">Unhealthy</p>
            <p className="text-3xl font-bold text-red-600">{health.unhealthy_containers}</p>
          </div>
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <p className="text-xs text-gray-600 mb-2">Total</p>
            <p className="text-3xl font-bold text-blue-600">{health.total_containers}</p>
          </div>
          <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
            <p className="text-xs text-gray-600 mb-2">Restarts</p>
            <p className="text-3xl font-bold text-yellow-600">{health.total_restarts}</p>
          </div>
        </div>
      )}

      {/* Throughput Trend */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Throughput Trend (24h)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={throughput}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="avg_rps" fill="#3b82f6" name="Avg RPS" />
            <Bar dataKey="max_rps" fill="#ef4444" name="Max RPS" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Containers by Service */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Containers by Service</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {byService.map((service, idx) => (
            <div key={idx} className="p-4 border rounded-lg">
              <div className="flex justify-between items-center mb-3">
                <span className="font-semibold">{service.service_name}</span>
                <span className="text-sm bg-blue-100 text-blue-700 px-2 py-1 rounded">
                  {service.container_count} containers
                </span>
              </div>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Healthy:</span>
                  <span className="font-semibold text-green-600">{service.healthy_count}</span>
                </div>
                <div className="flex justify-between">
                  <span>Avg Memory:</span>
                  <span className="font-semibold">{service.avg_memory?.toFixed(1) || 0}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Avg RPS:</span>
                  <span className="font-semibold">{service.avg_rps?.toFixed(0) || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>Total Restarts:</span>
                  <span className="font-semibold text-yellow-600">{service.total_restarts}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Restart Activity */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Container Restarts (24h)</h3>
        <DataTable
          columns={[
            { key: 'container_id', label: 'Container' },
            { key: 'service_name', label: 'Service' },
            { key: 'restart_count', label: 'Restarts', render: (v) => <span className="font-bold text-yellow-600">{v}</span> },
            { key: 'health', label: 'Health', render: (v) => <StatusBadge status={v} /> }
          ]}
          data={restarts}
          maxRows={20}
        />
      </div>

      {/* Current Containers */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Current Container States</h3>
        <DataTable
          columns={[
            { key: 'container_id', label: 'Container ID' },
            { key: 'service_name', label: 'Service' },
            { key: 'memory_utilization', label: 'Memory', render: (v) => `${v.toFixed(1)}%` },
            { key: 'requests_per_sec', label: 'RPS', render: (v) => v.toFixed(0) },
            { key: 'health', label: 'Health', render: (v) => <StatusBadge status={v} /> }
          ]}
          data={containers}
          maxRows={15}
        />
      </div>
    </div>
  )
}
