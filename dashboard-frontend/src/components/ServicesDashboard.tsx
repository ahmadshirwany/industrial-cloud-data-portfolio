import React, { useEffect, useState } from 'react'
import { apiService } from '../services/api'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart } from 'recharts'

export const ServicesDashboard: React.FC = () => {
  const [performance, setPerformance] = useState<any[]>([])
  const [latencyTrend, setLatencyTrend] = useState<any[]>([])
  const [errorRateTrend, setErrorRateTrend] = useState<any[]>([])
  const [successRateGauge, setSuccessRateGauge] = useState<any[]>([])
  const [slowestServices, setSlowestServices] = useState<any[]>([])
  const [failedRequests, setFailedRequests] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [perf, latency, errorRate, successRate, slowest, failed] = await Promise.all([
          apiService.getServicePerformance(1),
          apiService.getLatencyTrend(24),
          apiService.getErrorRateTrend(24),
          apiService.getSuccessRateGauge(5),
          apiService.getSlowestServices(5),
          apiService.getFailedRequests(24)
        ])

        setServices(Array.isArray(perf.data) ? perf.data : [])
        setLatencyTrend(Array.isArray(latency.data) ? latency.data : [])
        setErrorTrend(Array.isArray(errorRate.data) ? errorRate.data : [])
        setFailures(Array.isArray(failed.data) ? failed.data : [])
      } catch (err) {
        console.error('Failed to fetch service data', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 60000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <div>Loading service metrics...</div>

  return (
    <div className="space-y-6">
      {/* Latency Trend */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Response Time Trend</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={latencyTrend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="avg_latency" stroke="#3b82f6" name="Avg Latency (ms)" />
            <Line type="monotone" dataKey="p95_latency" stroke="#ef4444" name="P95 Latency (ms)" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Error Rate Trend */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Error Rate Trend</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={errorTrend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="avg_error_rate" fill="#ef4444" name="Error Rate %" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Service Performance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Service Performance</h3>
          <div className="space-y-4">
            {services.map((service, idx) => (
              <div key={idx} className="p-4 border rounded-lg hover:bg-gray-50">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold">{service.service_name}</span>
                  <span className="text-sm text-gray-600">{service.avg_success_rate?.toFixed(1) || 0}%</span>
                </div>
                <ProgressBar value={service.avg_success_rate || 0} max={100} color="green" />
                <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-gray-600">
                  <div>
                    <p>Avg Latency</p>
                    <p className="font-semibold text-gray-900">{service.avg_response_time?.toFixed(0) || 0}ms</p>
                  </div>
                  <div>
                    <p>Error Rate</p>
                    <p className="font-semibold text-gray-900">{service.avg_error_rate?.toFixed(1) || 0}%</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Failed Requests */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Failed Requests Summary</h3>
          <div className="space-y-3">
            {failures.map((service, idx) => (
              <div key={idx} className="p-3 border rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-sm">{service.service_name}</span>
                  <span className="text-sm font-bold text-red-600">{service.total_failures.toLocaleString()}</span>
                </div>
                <div className="mt-2 text-xs text-gray-600">
                  <p>Total: {service.total_requests.toLocaleString()} | Error Rate: {service.avg_error_rate?.toFixed(2) || 0}%</p>
                </div>
                <ProgressBar value={service.avg_error_rate || 0} max={100} color="red" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Full Service Table */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Detailed Service Metrics</h3>
        <DataTable
          columns={[
            { key: 'service_name', label: 'Service' },
            { key: 'avg_success_rate', label: 'Success', render: (v) => `${v.toFixed(1)}%` },
            { key: 'avg_error_rate', label: 'Error Rate', render: (v) => `${v.toFixed(2)}%` },
            { key: 'avg_response_time', label: 'Avg Latency', render: (v) => `${v.toFixed(0)}ms` },
            { key: 'p95_response_time', label: 'P95 Latency', render: (v) => `${v.toFixed(0)}ms` },
            { key: 'total_requests', label: 'Requests', render: (v) => v.toLocaleString() }
          ]}
          data={services}
        />
      </div>
    </div>
  )
}
