import React, { useEffect, useState } from 'react'
import { apiService } from '../services/api'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { StatusBadge, DataTable } from './Common'

export const ServersDashboard: React.FC = () => {
  const [serverHealth, setServerHealth] = useState<any>(null)
  const [currentServers, setCurrentServers] = useState<any[]>([])
  const [cpuTrends, setCpuTrends] = useState<any[]>([])
  const [serversByRegion, setServersByRegion] = useState<any[]>([])
  const [topCpuServers, setTopCpuServers] = useState<any[]>([])
  const [diskUsage, setDiskUsage] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [health, current, trends, regions, topCpu, disk] = await Promise.all([
          apiService.getServerHealth(5),
          apiService.getCurrentServers(50),
          apiService.getCPUTrends(24, '15min'),
          apiService.getServersByRegion(),
          apiService.getTopCPUServers(10),
          apiService.getDiskUsage()
        ])

        setServerHealth(health.data || health)
        setCurrentServers(Array.isArray(current.data) ? current.data : [])
        setCpuTrends(Array.isArray(trends.data) ? trends.data : [])
        setServersByRegion(Array.isArray(regions.data) ? regions.data : [])
        setTopCpuServers(Array.isArray(topCpu.data) ? topCpu.data : [])
        setDiskUsage(Array.isArray(disk.data) ? disk.data : [])
        setError('')
      } catch (err) {
        setError('Failed to fetch server data')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 60000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return <div className="text-center py-12 text-gray-600">Loading servers...</div>
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-100 text-green-800'
      case 'warning': return 'bg-yellow-100 text-yellow-800'
      case 'critical': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Health Summary Cards */}
      {serverHealth && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="bg-green-50 rounded-lg p-4 border-l-4 border-green-500">
            <div className="text-sm text-gray-600">Healthy</div>
            <div className="text-2xl font-bold text-green-600 mt-1">{serverHealth.healthy_servers}</div>
            <div className="text-xs text-gray-500 mt-1">of {serverHealth.total_servers}</div>
          </div>
          <div className="bg-yellow-50 rounded-lg p-4 border-l-4 border-yellow-500">
            <div className="text-sm text-gray-600">Warning</div>
            <div className="text-2xl font-bold text-yellow-600 mt-1">{serverHealth.warning_servers}</div>
          </div>
          <div className="bg-red-50 rounded-lg p-4 border-l-4 border-red-500">
            <div className="text-sm text-gray-600">Critical</div>
            <div className="text-2xl font-bold text-red-600 mt-1">{serverHealth.critical_servers}</div>
          </div>
          <div className="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-500">
            <div className="text-sm text-gray-600">Avg CPU</div>
            <div className="text-2xl font-bold text-blue-600 mt-1">{serverHealth.avg_cpu.toFixed(1)}%</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 border-l-4 border-purple-500">
            <div className="text-sm text-gray-600">Avg Memory</div>
            <div className="text-2xl font-bold text-purple-600 mt-1">{serverHealth.avg_memory.toFixed(1)}%</div>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CPU Trends */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">CPU Trends (24 Hours)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={cpuTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="avg_cpu" stroke="#3b82f6" name="Avg CPU" />
              <Line type="monotone" dataKey="avg_memory" stroke="#ef4444" name="Avg Memory" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Servers by Region */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Servers by Region</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={serversByRegion}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="region" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="server_count" fill="#3b82f6" name="Server Count" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top CPU Servers */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Top CPU Consumers</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Server ID</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Region</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">CPU %</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {topCpuServers.slice(0, 10).map((server, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-3">{server.server_id}</td>
                  <td className="px-4 py-3">{server.region}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center">
                      <div className="w-full bg-gray-200 rounded-full h-2 mr-2 max-w-xs">
                        <div
                          className="bg-orange-500 h-2 rounded-full"
                          style={{ width: `${Math.min(server.cpu_percent, 100)}%` }}
                        ></div>
                      </div>
                      <span className="font-semibold text-gray-900">{server.cpu_percent.toFixed(1)}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(server.status)}`}>
                      {server.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Disk Usage */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Disk Usage (&gt;50%)</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Server ID</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Region</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Used / Total</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Utilization</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {diskUsage.map((disk, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-3">{disk.server_id}</td>
                  <td className="px-4 py-3">{disk.region}</td>
                  <td className="px-4 py-3 text-gray-600">{disk.disk_used_gb}GB / {disk.disk_total_gb}GB</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center">
                      <div className="w-full bg-gray-200 rounded-full h-2 mr-2 max-w-xs">
                        <div
                          className={`h-2 rounded-full ${disk.disk_utilization > 80 ? 'bg-red-500' : disk.disk_utilization > 60 ? 'bg-yellow-500' : 'bg-green-500'}`}
                          style={{ width: `${disk.disk_utilization}%` }}
                        ></div>
                      </div>
                      <span className="font-semibold text-gray-900">{disk.disk_utilization.toFixed(1)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
