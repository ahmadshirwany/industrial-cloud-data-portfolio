import React, { useEffect, useState } from 'react'
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { apiService } from '../services/api'

export const OverviewDashboard: React.FC = () => {
  const [systemHealth, setSystemHealth] = useState<any>(null)
  const [dailyStats, setDailyStats] = useState<any>(null)
  const [cpuTrends, setCpuTrends] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [health, stats, trends] = await Promise.all([
          apiService.getSystemHealth(5),
          apiService.getDailyStats(),
          apiService.getCPUTrends(1, '5min')
        ])

        console.log('=== RAW AXIOS RESPONSES ===')
        console.log('health response:', health)
        console.log('stats response:', stats)
        console.log('trends response:', trends)
        
        // Extract data from axios responses
        const healthData = health?.data ?? health
        const statsData = stats?.data ?? stats
        const trendsData = trends?.data ?? trends
        
        console.log('=== EXTRACTED DATA ===')
        console.log('healthData:', healthData)
        console.log('statsData:', statsData)
        console.log('trendsData:', trendsData)
        
        // Verify data before setting
        if (healthData && typeof healthData === 'object') {
          console.log('healthData is valid object with keys:', Object.keys(healthData))
        }
        if (statsData && typeof statsData === 'object') {
          console.log('statsData is valid object with keys:', Object.keys(statsData))
        }
        
        setSystemHealth(healthData)
        setDailyStats(statsData)
        setCpuTrends(Array.isArray(trendsData) ? trendsData : [])
        setError('')
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : String(err)
        console.error('FETCH ERROR:', err)
        console.error('Error message:', errorMsg)
        setError('Failed to fetch dashboard data: ' + errorMsg)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return <div className="text-center py-12 text-gray-600">Loading dashboard...</div>
  }

  const COLORS = ['#3b82f6', '#ef4444', '#f59e0b']

  const healthData = systemHealth ? [
    { name: 'Health Score', value: Math.round(systemHealth.score) },
    { name: 'Gap', value: 100 - Math.round(systemHealth.score) }
  ] : []

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* System Health Score */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">System Health Score</h3>
          <div className="text-center">
            <div className="text-6xl font-bold text-blue-600">
              {systemHealth?.score || 0}
            </div>
            <p className="text-gray-600 text-sm mt-2">out of 100</p>
            <div className="mt-4 space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span>CPU</span>
                <span className="font-semibold">{systemHealth?.avg_cpu?.toFixed(1) || 0}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{width: `${Math.min(systemHealth?.avg_cpu || 0, 100)}%`}}></div>
              </div>

              <div className="flex justify-between items-center text-sm mt-3">
                <span>Memory</span>
                <span className="font-semibold">{systemHealth?.avg_memory?.toFixed(1) || 0}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-yellow-500 h-2 rounded-full" style={{width: `${Math.min(systemHealth?.avg_memory || 0, 100)}%`}}></div>
              </div>

              <div className="flex justify-between items-center text-sm mt-3">
                <span>Disk</span>
                <span className="font-semibold">{systemHealth?.avg_disk?.toFixed(1) || 0}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-purple-500 h-2 rounded-full" style={{width: `${Math.min(systemHealth?.avg_disk || 0, 100)}%`}}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Key Metrics</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded">
              <span className="text-sm font-medium">Success Rate</span>
              <span className="text-2xl font-bold text-green-600">{systemHealth?.avg_success_rate?.toFixed(1) || 0}%</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-yellow-50 rounded">
              <span className="text-sm font-medium">Critical Servers</span>
              <span className="text-2xl font-bold text-red-600">{systemHealth?.critical_servers || 0}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-purple-50 rounded">
              <span className="text-sm font-medium">Total Requests</span>
              <span className="text-2xl font-bold text-purple-600">{(dailyStats?.total_requests || 0) / 1000000 > 0 ? (dailyStats?.total_requests || 0) / 1000000 : 0}M</span>
            </div>
            <div className="border-t pt-3 mt-3">
              <p className="text-sm text-gray-600">
                Total Servers: <span className="font-bold text-gray-900">{dailyStats?.total_servers || 0}</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Daily Statistics */}
      {dailyStats && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">24-Hour Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-xs text-gray-600 mb-1">Total Servers</p>
              <p className="text-2xl font-bold text-blue-600">{dailyStats.total_servers}</p>
            </div>
            <div className="p-4 bg-yellow-50 rounded-lg">
              <p className="text-xs text-gray-600 mb-1">Total Restarts</p>
              <p className="text-2xl font-bold text-yellow-600">{dailyStats.total_restarts}</p>
            </div>
            <div className="p-4 bg-red-50 rounded-lg">
              <p className="text-xs text-gray-600 mb-1">Total Requests</p>
              <p className="text-2xl font-bold text-red-600">{(dailyStats.total_requests / 1000000).toFixed(1)}M</p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-xs text-gray-600 mb-1">Success Rate</p>
              <p className="text-2xl font-bold text-green-600">{dailyStats.avg_success_rate?.toFixed(1) || 0}%</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
