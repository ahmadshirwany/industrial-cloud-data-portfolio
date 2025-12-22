import React, { useEffect, useState } from 'react'
import { AreaChart, Area, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { apiService } from '../services/api'
import { StatusBadge } from './Common'

const COLORS = ['#3b82f6', '#ef4444', '#f97316', '#eab308', '#10b981']

export const AnalyticsDashboard: React.FC = () => {
  const [health, setHealth] = useState<any>(null)
  const [anomalies, setAnomalies] = useState<any[]>([])
  const [forecast, setForecast] = useState<any[]>([])
  const [regional, setRegional] = useState<any[]>([])
  const [topErrors, setTopErrors] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [healthRes, anomaliesRes, forecastRes, regionalRes, errorsRes] = await Promise.all([
          apiService.getSystemHealth(),
          apiService.getAnomalies(),
          apiService.getCapacityForecast(7),
          apiService.getRegionalSummary(),
          apiService.getTopErrorServices(10)
        ])

        setHealth(healthRes.data || healthRes)
        setAnomalies(Array.isArray(anomaliesRes.data) ? anomaliesRes.data : [])
        setForecast(Array.isArray(forecastRes.data) ? forecastRes.data : [])
        setRegional(Array.isArray(regionalRes.data) ? regionalRes.data : [])
        setTopErrors(Array.isArray(errorsRes.data) ? errorsRes.data : [])
      } catch (err) {
        console.error('Failed to fetch analytics data', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 120000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <div>Loading analytics...</div>

  return (
    <div className="space-y-6">
      {/* System Health Score */}
      {health && (
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg shadow-lg p-8 text-white">
          <p className="text-sm opacity-90 mb-2">System Health Score</p>
          <div className="flex items-end gap-4">
            <div className="text-6xl font-bold">{health.overall_health?.toFixed(0) || 0}</div>
            <div className="text-lg opacity-90 pb-2">/100</div>
          </div>
          <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="opacity-75">Uptime</p>
              <p className="text-xl font-semibold">{health.uptime_percent?.toFixed(1) || 0}%</p>
            </div>
            <div>
              <p className="opacity-75">Avg Response</p>
              <p className="text-xl font-semibold">{health.avg_response_time?.toFixed(0) || 0}ms</p>
            </div>
            <div>
              <p className="opacity-75">Success Rate</p>
              <p className="text-xl font-semibold">{health.success_rate_percent?.toFixed(1) || 0}%</p>
            </div>
          </div>
        </div>
      )}

      {/* Capacity Forecast */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">7-Day Capacity Forecast</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={forecast}>
            <defs>
              <linearGradient id="colorCPU" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorMemory" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Area type="monotone" dataKey="predicted_cpu" stroke="#3b82f6" fillOpacity={1} fill="url(#colorCPU)" name="CPU %" />
            <Area type="monotone" dataKey="predicted_memory" stroke="#ef4444" fillOpacity={1} fill="url(#colorMemory)" name="Memory %" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Regional Distribution */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Regional Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={regional}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ region, servers }) => `${region}: ${servers}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="servers"
              >
                {regional.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Top Error Services */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Top Error Services</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart
              layout="vertical"
              data={topErrors}
              margin={{ top: 5, right: 30, left: 200, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="service_name" type="category" width={190} />
              <Tooltip />
              <Bar dataKey="total_errors" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Anomalies Alert */}
      {anomalies.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <h3 className="text-lg font-semibold">Active Anomalies ({anomalies.length})</h3>
          </div>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {anomalies.map((anomaly, idx) => (
              <div key={idx} className="p-3 bg-red-50 rounded-lg border border-red-200">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-semibold text-red-900">{anomaly.metric_name}</p>
                    <p className="text-sm text-red-700">{anomaly.anomaly_type}</p>
                  </div>
                  <span className="text-xs bg-red-200 text-red-800 px-2 py-1 rounded">
                    {anomaly.severity}
                  </span>
                </div>
                <p className="text-xs text-red-600">{anomaly.description}</p>
                {anomaly.detected_at && (
                  <p className="text-xs text-gray-500 mt-2">
                    Detected: {new Date(anomaly.detected_at).toLocaleString()}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {anomalies.length === 0 && (
        <div className="bg-green-50 rounded-lg p-6 border border-green-200">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <p className="text-green-700 font-semibold">No anomalies detected - System operating normally</p>
          </div>
        </div>
      )}
    </div>
  )
}
