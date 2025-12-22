import React, { useState } from 'react'
import { OverviewDashboard } from './components/OverviewDashboard'
import { ServersDashboard } from './components/ServersDashboard'
import { ServicesDashboard } from './components/ServicesDashboard'
import { ContainersDashboard } from './components/ContainersDashboard'
import { AnalyticsDashboard } from './components/AnalyticsDashboard'

type DashboardView = 'overview' | 'servers' | 'services' | 'containers' | 'analytics'

const NAV_ITEMS: { id: DashboardView; label: string; icon: string }[] = [
  { id: 'overview', label: 'Overview', icon: '📊' },
  { id: 'servers', label: 'Servers', icon: '🖥️' },
  { id: 'services', label: 'Services', icon: '⚙️' },
  { id: 'containers', label: 'Containers', icon: '📦' },
  { id: 'analytics', label: 'Analytics', icon: '📈' }
]

function App() {
  const [activeView, setActiveView] = useState<DashboardView>('overview')

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-3xl font-bold text-gray-900">Industrial Cloud Dashboard</h1>
          <p className="text-sm text-gray-600 mt-1">Real-time monitoring and analytics</p>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1 overflow-x-auto">
            {NAV_ITEMS.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveView(item.id)}
                className={`px-6 py-4 font-medium transition-colors whitespace-nowrap ${
                  activeView === item.id
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {activeView === 'overview' && <OverviewDashboard />}
        {activeView === 'servers' && <ServersDashboard />}
        {activeView === 'services' && <ServicesDashboard />}
        {activeView === 'containers' && <ContainersDashboard />}
        {activeView === 'analytics' && <AnalyticsDashboard />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-6 py-6 text-center text-sm text-gray-600">
          <p>Industrial Cloud Data Portfolio • Real-time metrics updated every 30-120 seconds</p>
        </div>
      </footer>
    </div>
  )
}

export default App
