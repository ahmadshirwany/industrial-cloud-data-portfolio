# Dashboard Frontend

React + TypeScript + Vite + Recharts dashboard for monitoring industrial cloud telemetry data.

## Features

- 📊 **Real-time Dashboard** - System health overview with key metrics
- 🖥️ **Server Monitoring** - CPU, memory, and regional server distribution
- ⚙️ **Service Metrics** - Service performance, latency trends, error rates
- 📦 **Container Management** - Container health, throughput, and restart tracking
- 📈 **Advanced Analytics** - System health scores, anomaly detection, capacity forecasting
- 🔄 **Live Updates** - Auto-refresh dashboards every 30-120 seconds
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices
- ⚡ **Type-Safe** - Full TypeScript support with strict mode

## Project Structure

```
dashboard-frontend/
├── src/
│   ├── components/
│   │   ├── Common.tsx                 # Reusable UI components
│   │   ├── OverviewDashboard.tsx      # System health overview
│   │   ├── ServersDashboard.tsx       # Server metrics
│   │   ├── ServicesDashboard.tsx      # Service performance
│   │   ├── ContainersDashboard.tsx    # Container management
│   │   └── AnalyticsDashboard.tsx     # Advanced analytics
│   ├── services/
│   │   └── api.ts                     # API integration layer
│   ├── types/
│   │   └── api.ts                     # TypeScript interfaces
│   ├── App.tsx                        # Main application
│   ├── main.tsx                       # Entry point
│   └── index.css                      # Global styles
├── index.html                         # HTML entry point
├── package.json                       # Dependencies
├── tsconfig.json                      # TypeScript config
├── vite.config.ts                     # Vite configuration
├── tailwind.config.js                 # Tailwind CSS config
└── postcss.config.js                  # PostCSS config
```

## Getting Started

### Prerequisites

- **Node.js** 16.0.0 or higher
- **npm** 7.0.0 or higher
- **Backend Service** running on `http://localhost:8080` (FastAPI Dashboard API)

### Installation

1. **Install dependencies**

```bash
cd dashboard-frontend
npm install
```

This will install all required packages:
- React 18
- React DOM 18
- TypeScript 5
- Vite 5
- Recharts 2 (data visualization)
- Axios 1 (HTTP client)
- date-fns (date utilities)
- Tailwind CSS (styling)

### Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

**Important**: The development server includes an API proxy that forwards requests from `http://localhost:5173/api/*` to `http://localhost:8080/api/*`. Make sure your backend is running on port 8080.

### Build for Production

Build the application for production:

```bash
npm run build
```

This creates an optimized build in the `dist` folder.

### Preview Production Build

Preview the production build locally:

```bash
npm run preview
```

## API Integration

The dashboard connects to the FastAPI backend via the API service wrapper (`src/services/api.ts`).

### Available Endpoints

All endpoints are accessed through the `apiService` object:

**Servers (6 endpoints)**
- `getServerHealth(minutes)` - Server CPU and memory trends
- `getCurrentServers()` - Current server states
- `getServersByRegion()` - Regional distribution
- `getTopCpuServers(limit)` - High CPU servers
- `getServerDiskUsage()` - Disk space utilization
- `getServerUptimeSummary()` - Server uptime statistics

**Containers (6 endpoints)**
- `getContainerHealth()` - Container health summary
- `getCurrentContainers(limit)` - Current container states
- `getContainersByService()` - Containers grouped by service
- `getContainerRestarts(hours)` - Container restart activity
- `getThroughputTrend(hours)` - Throughput metrics
- `getHighMemoryContainers(limit)` - High memory consumers

**Services (8 endpoints)**
- `getServiceHealth()` - Service health overview
- `getServicePerformance()` - Service metrics
- `getLatencyTrend(hours)` - Response time trends
- `getErrorRateTrend(hours)` - Error rate trends
- `getFailedRequests(limit)` - Failed requests by service
- `getTopErrorServices(limit)` - Services with most errors
- `getServiceAvailability(hours)` - Service availability
- `getServiceLatencyPercentiles()` - Latency percentiles

**Analytics (7 endpoints)**
- `getSystemHealth()` - Overall system health score
- `getAnomalies()` - Detected anomalies
- `getCapacityForecast(days)` - CPU/Memory forecast
- `getRegionalSummary()` - Regional statistics
- `getHealthTrend(hours)` - Health score trend
- `getDailyStats(days)` - Daily statistics
- `getWebSocketMetrics()` - WebSocket performance

### Example API Usage

```typescript
import { apiService } from '../services/api'

// Fetch server health
const response = await apiService.getServerHealth(5)
console.log(response.data) // Array of server metrics

// Fetch with error handling
try {
  const servers = await apiService.getCurrentServers()
  setServers(servers.data)
} catch (error) {
  console.error('Failed to fetch servers', error)
}
```

## Components

### Common Components (`src/components/Common.tsx`)

Reusable UI components used across dashboards:

1. **StatCard** - Metric display with trend indicators
   - Props: `label`, `value`, `unit`, `trend`, `color`, `icon`
   - Example: Shows CPU usage with trend arrow

2. **StatusBadge** - Health status indicator
   - Props: `status` (healthy|warning|critical)
   - Shows color-coded status with icon

3. **ProgressBar** - Visual percentage indicator
   - Props: `value` (0-100), `label`, `color`
   - Filled bar with percentage text

4. **DataTable** - Sortable data display
   - Props: `columns`, `data`, `maxRows`
   - Supports custom cell rendering

### Dashboard Components

1. **OverviewDashboard** - System-wide health overview
   - System health score
   - Server status distribution
   - Resource utilization gauges
   - 24-hour statistics

2. **ServersDashboard** - Server-level monitoring
   - CPU & Memory trends (AreaChart)
   - Regional distribution
   - Top CPU consumers
   - Disk usage by server

3. **ServicesDashboard** - Service performance tracking
   - Response time trends (LineChart)
   - Error rate trends (BarChart)
   - Failed requests summary
   - Service performance cards

4. **ContainersDashboard** - Container lifecycle management
   - Container health summary
   - Containers by service
   - Throughput trends
   - Restart activity tracking

5. **AnalyticsDashboard** - Advanced monitoring and forecasting
   - System health score card
   - 7-day capacity forecast
   - Regional distribution (PieChart)
   - Top error services (BarChart)
   - Active anomalies alert

## Styling

The project uses **Tailwind CSS** for styling with custom theme colors:

- **Primary**: Blue (`#3b82f6`)
- **Secondary**: Green (`#10b981`)
- **Warning**: Amber (`#f59e0b`)
- **Danger**: Red (`#ef4444`)

Custom CSS variables and utilities are defined in `src/index.css`.

### Responsive Design

All components are responsive with mobile-first approach:
- Mobile: Single column layout
- Tablet: 2-column grid
- Desktop: Multi-column grid and full charts

## Data Visualization

**Recharts** library is used for all charts:

- **AreaChart** - Trend visualization (CPU, Memory)
- **BarChart** - Categorical comparisons (Errors, Restarts)
- **LineChart** - Time series (Latency, Error rates)
- **PieChart** - Distribution visualization (Regional split)

All charts include:
- Tooltips on hover
- Legend for data series
- Responsive sizing
- Custom colors

## Real-Time Updates

Dashboards auto-refresh data at intervals:

- **Overview**: 30 seconds
- **Servers**: 30 seconds
- **Services**: 30 seconds
- **Containers**: 60 seconds
- **Analytics**: 120 seconds

Refresh intervals are configurable in component `useEffect` hooks.

## Error Handling

The API service includes error handling:

```typescript
try {
  const data = await apiService.getServerHealth(5)
  setMetrics(data.data)
} catch (error) {
  console.error('API Error:', error)
  setError('Failed to load data')
}
```

## Performance Optimization

- **Lazy loading** - Components load data only when visible
- **Memoization** - Components re-render only on data changes
- **Code splitting** - Vite automatically splits code for faster loading
- **Chart optimization** - Recharts uses virtual rendering for large datasets

## Development Tips

### Adding a New Dashboard

1. Create new component in `src/components/`
2. Define TypeScript interfaces in `src/types/api.ts`
3. Add API methods to `src/services/api.ts`
4. Add navigation item in `App.tsx`

### Modifying the API Service

Update `src/services/api.ts` to add or modify endpoints:

```typescript
// Example: Add new endpoint
export const apiService = {
  // ... existing endpoints
  getNewMetric: () =>
    api.get<ResponseType>('/new-endpoint'),
}
```

### Custom Styling

Add custom Tailwind styles in `src/index.css`:

```css
@layer components {
  .custom-card {
    @apply rounded-lg shadow-md p-6 bg-white;
  }
}
```

## Deployment

### Build for Production

```bash
npm run build
```

Output is in the `dist` folder, which can be deployed to:
- Vercel
- Netlify
- GitHub Pages
- Cloud Storage (GCS, S3)
- Docker container

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:

```bash
docker build -t dashboard-frontend .
docker run -p 80:80 dashboard-frontend
```

## Troubleshooting

### API Connection Issues

**Problem**: `Cannot POST /api/...`
**Solution**: Ensure backend is running on `http://localhost:8080`

**Problem**: CORS errors
**Solution**: Backend must have CORS enabled (check dashboard-api `main.py`)

### Build Errors

**Problem**: `Module not found`
**Solution**: Run `npm install` to ensure all dependencies are installed

**Problem**: TypeScript errors
**Solution**: Check `tsconfig.json` configuration and ensure types are installed

### Performance Issues

**Problem**: Slow chart rendering
**Solution**: Reduce data points or use `debounce` for refresh intervals

**Problem**: High memory usage
**Solution**: Clear browser cache and reduce auto-refresh frequency

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Environment Variables

Create `.env` file in project root:

```env
VITE_API_URL=http://localhost:8080
VITE_API_TIMEOUT=5000
```

Access in code:

```typescript
const apiUrl = import.meta.env.VITE_API_URL
```

## Contributing

1. Create a new branch for features
2. Follow Prettier formatting (auto-applied on save)
3. Write TypeScript with strict mode enabled
4. Test components in multiple browsers

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation in backend repo
3. Check console logs for error messages

## Next Steps

- Configure backend service (see `../services/dashboard-api/README.md`)
- Set up Docker containers
- Deploy to cloud platform
- Configure monitoring alerts
- Set up CI/CD pipeline
