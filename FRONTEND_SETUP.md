# Dashboard Frontend - Setup & Deployment Guide

## Quick Start

### 1. Install Node.js (if not already installed)

Download and install from https://nodejs.org/ (LTS recommended)

Verify installation:
```bash
node --version
npm --version
```

### 2. Install Dependencies

```bash
cd dashboard-frontend
npm install
```

### 3. Start Development Server

```bash
npm run dev
```

Open browser: `http://localhost:5173`

**Important**: Ensure the FastAPI backend is running on `http://localhost:8080`

## Development Workflow

### Available Commands

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Check TypeScript
npm run typecheck  # if added to package.json

# Format code (if Prettier is configured)
npm run format
```

### Project Structure Overview

```
dashboard-frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Common.tsx       # Reusable UI components
│   │   ├── OverviewDashboard.tsx
│   │   ├── ServersDashboard.tsx
│   │   ├── ServicesDashboard.tsx
│   │   ├── ContainersDashboard.tsx
│   │   └── AnalyticsDashboard.tsx
│   ├── services/
│   │   └── api.ts           # API integration
│   ├── types/
│   │   └── api.ts           # TypeScript types
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── index.html               # HTML template
├── package.json             # Dependencies
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript config
├── tailwind.config.js       # Tailwind config
└── postcss.config.js        # PostCSS config
```

## Backend Integration

### API Proxy Configuration

The development server proxies API requests to the backend:

- **Frontend**: `http://localhost:5173/api/*`
- **Backend**: `http://localhost:8080/api/*`

This is configured in `vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true
    }
  }
}
```

### Required Backend Services

Ensure the FastAPI backend is running:

```bash
cd ../services/dashboard-api
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

## Deployment Options

### Option 1: Docker Deployment

#### Create Dockerfile

Already included in repository (create if not exists):

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Create nginx.conf

```nginx
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    location /api {
        proxy_pass http://backend:8080;
    }
}
```

#### Build & Run Docker Container

```bash
# Build image
docker build -t dashboard-frontend:latest .

# Run container
docker run -p 3000:80 dashboard-frontend:latest

# Access at http://localhost:3000
```

### Option 2: Vercel Deployment

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
vercel
```

3. Configure environment variables in Vercel dashboard:
```
VITE_API_URL=https://api.example.com
```

### Option 3: Netlify Deployment

1. Build the project:
```bash
npm run build
```

2. Deploy `dist` folder via Netlify:
   - Connect repository
   - Build command: `npm run build`
   - Publish directory: `dist`

3. Configure API proxy in `netlify.toml`:

```toml
[[redirects]]
from = "/api/*"
to = "https://api.example.com/api/:splat"
status = 200
```

### Option 4: Cloud Storage (GCS/S3)

#### Build for Production

```bash
npm run build
```

#### Upload to GCS

```bash
gsutil -m cp -r dist/* gs://your-bucket/
```

#### Upload to S3

```bash
aws s3 sync dist/ s3://your-bucket/
```

### Option 5: Traditional Web Server (Nginx/Apache)

#### Build for Production

```bash
npm run build
```

#### Copy Files to Server

```bash
scp -r dist/* user@server:/var/www/html/dashboard/
```

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name dashboard.example.com;

    location / {
        root /var/www/html/dashboard;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend-server:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Environment Configuration

### Development Environment

Create `.env.local`:

```env
VITE_API_URL=http://localhost:8080
VITE_API_TIMEOUT=5000
VITE_REFRESH_INTERVAL=30000
```

### Production Environment

Create `.env.production`:

```env
VITE_API_URL=https://api.example.com
VITE_API_TIMEOUT=10000
VITE_REFRESH_INTERVAL=60000
```

### Access Environment Variables

```typescript
const apiUrl = import.meta.env.VITE_API_URL
```

## Performance Optimization

### 1. Build Optimization

```bash
npm run build

# Check bundle size
npm install -g webpack-bundle-analyzer
```

### 2. Caching Strategy

Configure in web server:

**Nginx**:
```nginx
location ~* \.(js|css|png|jpg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. Compression

Enable gzip compression:

**Nginx**:
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

## Monitoring & Logging

### Client-Side Logging

Add error tracking (e.g., Sentry):

```typescript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "YOUR_SENTRY_DSN",
  environment: import.meta.env.MODE,
});
```

### Analytics

Add Google Analytics:

```typescript
import ReactGA from 'react-ga';

ReactGA.initialize('GA_MEASUREMENT_ID');
```

## Troubleshooting Deployment

### Issue: Blank Page After Deployment

**Cause**: HTML loading CSS/JS from wrong path
**Solution**: Check `vite.config.ts` base path:

```typescript
export default defineConfig({
  base: '/dashboard/',  // if deployed in subdirectory
})
```

### Issue: API Calls Fail in Production

**Cause**: API proxy not configured or backend URL wrong
**Solution**: 
1. Check `VITE_API_URL` environment variable
2. Verify backend is accessible from frontend server
3. Check CORS configuration in backend

### Issue: 404 on Page Refresh

**Cause**: Server doesn't redirect to index.html
**Solution**: Configure fallback to index.html in web server

## Database Connection (Optional)

If frontend needs direct database access (not recommended):

```typescript
// .env
VITE_DATABASE_URL=postgresql://user:pass@host:5432/db
```

**Security Note**: Always use backend API for database access, never expose connection strings to frontend.

## Security Considerations

### 1. Environment Variables

Never commit `.env` files:
```bash
# Add to .gitignore
.env
.env.local
.env.*.local
```

### 2. API Security

- Use HTTPS in production
- Implement CORS properly
- Validate all API responses
- Use secure tokens for authentication

### 3. Content Security Policy

Add CSP headers (via web server or meta tag):

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self' 'unsafe-inline'">
```

## Continuous Integration/Deployment

### GitHub Actions Example

```yaml
name: Deploy Frontend

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm run build
      - run: npx vercel --prod --token ${{ secrets.VERCEL_TOKEN }}
```

## Scaling Considerations

### 1. CDN Integration

Use CDN for static assets:

```typescript
// vite.config.ts
export default defineConfig({
  base: 'https://cdn.example.com/dashboard/',
})
```

### 2. Load Balancing

For high traffic:
- Deploy multiple instances behind load balancer
- Use sticky sessions for WebSocket connections

### 3. Database Optimization

- Add database indices
- Implement caching (Redis)
- Paginate large datasets

## Support & Resources

- **Vite Docs**: https://vitejs.dev/
- **React Docs**: https://react.dev/
- **Recharts Docs**: https://recharts.org/
- **Tailwind CSS**: https://tailwindcss.com/

## Next Steps

1. ✅ Install Node.js and dependencies
2. ✅ Start development server
3. ✅ Verify backend integration
4. ✅ Test all dashboard views
5. ⏳ Build for production
6. ⏳ Deploy to chosen platform
7. ⏳ Set up monitoring
8. ⏳ Configure CI/CD pipeline
