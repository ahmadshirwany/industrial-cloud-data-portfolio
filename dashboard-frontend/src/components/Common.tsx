import React from 'react'

interface LoadingProps {
  message?: string
}

export const Loading: React.FC<LoadingProps> = ({ message = 'Loading...' }) => (
  <div className="flex justify-center items-center py-12">
    <div className="text-center">
      <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      <p className="mt-4 text-gray-600">{message}</p>
    </div>
  </div>
)

interface ErrorAlertProps {
  message: string
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ message }) => (
  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
    <p className="font-semibold">Error</p>
    <p className="text-sm mt-1">{message}</p>
  </div>
)

interface StatCardProps {
  label: string
  value: string | number
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple'
  trend?: {
    direction: 'up' | 'down'
    value: number
  }
}

export const StatCard: React.FC<StatCardProps> = ({ label, value, color = 'blue', trend }) => {
  const colorClasses = {
    blue: 'border-blue-500 bg-blue-50',
    green: 'border-green-500 bg-green-50',
    yellow: 'border-yellow-500 bg-yellow-50',
    red: 'border-red-500 bg-red-50',
    purple: 'border-purple-500 bg-purple-50'
  }

  const textColorClasses = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    yellow: 'text-yellow-600',
    red: 'text-red-600',
    purple: 'text-purple-600'
  }

  return (
    <div className={`rounded-lg p-4 border-l-4 ${colorClasses[color]}`}>
      <div className="text-sm text-gray-600">{label}</div>
      <div className={`text-2xl font-bold mt-1 ${textColorClasses[color]}`}>{value}</div>
      {trend && (
        <div className="text-xs mt-2 flex items-center">
          <span className={trend.direction === 'up' ? 'text-red-600' : 'text-green-600'}>
            {trend.direction === 'up' ? '↑' : '↓'} {trend.value}%
          </span>
        </div>
      )}
    </div>
  )
}

interface BadgeProps {
  label: string
  color?: 'green' | 'yellow' | 'red' | 'blue'
}

export const Badge: React.FC<BadgeProps> = ({ label, color = 'blue' }) => {
  const colorClasses = {
    green: 'bg-green-100 text-green-800',
    yellow: 'bg-yellow-100 text-yellow-800',
    red: 'bg-red-100 text-red-800',
    blue: 'bg-blue-100 text-blue-800'
  }

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${colorClasses[color]}`}>
      {label}
    </span>
  )
}

interface StatCardAdvancedProps {
  title: string
  value: string | number
  unit?: string
  icon?: React.ReactNode
  trend?: 'up' | 'down' | 'stable'
  color?: 'blue' | 'green' | 'red' | 'yellow'
}

export const StatCardAdvanced: React.FC<StatCardAdvancedProps> = ({
  title,
  value,
  unit,
  icon,
  trend,
  color = 'blue'
}) => {
  const colorClasses = {
    blue: 'from-blue-50 to-blue-100 border-blue-200',
    green: 'from-green-50 to-green-100 border-green-200',
    red: 'from-red-50 to-red-100 border-red-200',
    yellow: 'from-yellow-50 to-yellow-100 border-yellow-200'
  }

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <div className="mt-2 flex items-baseline">
            <span className="text-3xl font-bold text-gray-900">{value}</span>
            {unit && <span className="ml-2 text-sm text-gray-600">{unit}</span>}
          </div>
          {trend && (
            <div className="mt-2 text-xs font-semibold">
              {trend === 'up' && <span className="text-red-600">↑ Increasing</span>}
              {trend === 'down' && <span className="text-green-600">↓ Decreasing</span>}
              {trend === 'stable' && <span className="text-blue-600">→ Stable</span>}
            </div>
          )}
        </div>
        {icon && <div className="text-4xl opacity-20">{icon}</div>}
      </div>
    </div>
  )
}

interface StatusBadgeProps {
  status: 'healthy' | 'warning' | 'critical' | 'degraded' | 'unhealthy'
  label?: string
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label }) => {
  const config = {
    healthy: { bg: 'bg-green-100', text: 'text-green-800', icon: CheckCircle },
    warning: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: AlertTriangle },
    critical: { bg: 'bg-red-100', text: 'text-red-800', icon: AlertCircle },
    degraded: { bg: 'bg-orange-100', text: 'text-orange-800', icon: AlertTriangle },
    unhealthy: { bg: 'bg-red-100', text: 'text-red-800', icon: AlertCircle }
  }

  const { bg, text, icon: Icon } = config[status]

  return (
    <div className={`inline-flex items-center gap-1 px-3 py-1 rounded-full ${bg} ${text} text-xs font-semibold`}>
      <Icon size={14} />
      {label || status.charAt(0).toUpperCase() + status.slice(1)}
    </div>
  )
}

interface ProgressBarProps {
  value: number
  max?: number
  color?: 'blue' | 'green' | 'red' | 'yellow'
  showLabel?: boolean
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  color = 'blue',
  showLabel = true
}) => {
  const percentage = (value / max) * 100
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    red: 'bg-red-500',
    yellow: 'bg-yellow-500'
  }

  let barColor = color
  if (percentage > 80) barColor = 'red'
  else if (percentage > 60) barColor = 'yellow'

  return (
    <div className="w-full">
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${colorClasses[barColor]} transition-all duration-300`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
      {showLabel && (
        <p className="text-xs text-gray-600 mt-1">{percentage.toFixed(1)}%</p>
      )}
    </div>
  )
}

interface DataTableProps {
  columns: { key: string; label: string; render?: (value: any) => React.ReactNode }[]
  data: any[]
  maxRows?: number
  loading?: boolean
}

export const DataTable: React.FC<DataTableProps> = ({
  columns,
  data,
  maxRows = 10,
  loading = false
}) => {
  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin text-blue-500">⟳</div>
      </div>
    )
  }

  const displayData = data.slice(0, maxRows)

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b bg-gray-50">
            {columns.map(col => (
              <th key={col.key} className="px-4 py-3 text-left font-semibold text-gray-700">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {displayData.map((row, idx) => (
            <tr key={idx} className="border-b hover:bg-gray-50 transition-colors">
              {columns.map(col => (
                <td key={`${idx}-${col.key}`} className="px-4 py-3 text-gray-700">
                  {col.render ? col.render(row[col.key]) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {displayData.length === 0 && (
        <div className="text-center py-8 text-gray-500">No data available</div>
      )}
    </div>
  )
}
