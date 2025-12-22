# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files from dashboard-frontend directory
COPY dashboard-frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY dashboard-frontend/src ./src
COPY dashboard-frontend/index.html ./
COPY dashboard-frontend/postcss.config.js ./
COPY dashboard-frontend/tailwind.config.js ./
COPY dashboard-frontend/tsconfig.json ./
COPY dashboard-frontend/tsconfig.node.json ./
COPY dashboard-frontend/vite.config.ts ./

# Build the React app
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install serve to run the static app
RUN npm install -g serve

# Copy built app from build stage
COPY --from=build /app/dist ./dist

# Expose port for frontend
EXPOSE 5173

# Default command to serve the app
CMD ["serve", "-s", "dist", "-l", "5173"]
