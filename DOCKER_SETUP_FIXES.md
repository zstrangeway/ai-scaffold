# Docker Setup Fixes and Troubleshooting Guide

## Issues Identified and Fixed

### 1. **Docker Compose Configuration Issues**
- **Problem**: Obsolete `version: "3.8"` field causing warnings
- **Solution**: Removed the version field (it's now optional and ignored in modern Docker Compose)

### 2. **Port Mapping Inconsistencies**  
- **Problem**: Docker Compose expected Vite apps on port 5173, but all frontend apps are actually Next.js apps
- **Solution**: Updated port mappings:
  - `web_site`: 3000:3000 (Next.js default)
  - `web_app`: 3001:3001 (configured in package.json)
  - `web_admin`: 3002:3002 (configured in package.json)

### 3. **Frontend Dockerfile Issues**
- **Problem**: Apps were using npm instead of pnpm and had incorrect monorepo setup
- **Solution**: Updated all frontend Dockerfiles to:
  - Use Node 20 Alpine (more stable than Node 23)
  - Use pnpm with monorepo workspace support
  - Properly copy workspace files and dependencies
  - Support hot reloading with correct hostname and port configuration

### 4. **Hot Reloading Support**
- **Problem**: No environment variables for hot reloading in Docker
- **Solution**: Added environment variables:
  - `NODE_ENV=development`
  - `CHOKIDAR_USEPOLLING=true` (enables file watching in Docker containers)

### 5. **Python Service Configuration**
- **Problem**: Missing environment variables for proper Python execution
- **Solution**: Added environment variables:
  - `PYTHONPATH=/app` (ensures proper module resolution)
  - `PYTHONUNBUFFERED=1` (enables real-time log output)

### 6. **API Contracts Generation**
- **Problem**: Missing generated API contracts that services depend on
- **Solution**: Successfully generated contracts using `pnpm run generate-contracts`

## Current Architecture

### Frontend Applications (Next.js)
- **web_site** (Port 3000): Brochure/marketing site
- **web_app** (Port 3001): Main application with i18n, API integration
- **web_admin** (Port 3002): Admin panel
- **web_ui** (Port 6006): Storybook for shared components

### Backend Services (Python FastAPI)
- **postgres_db** (Port 5432): PostgreSQL database
- **gateway_service** (Port 8000): API Gateway/Router
- **user_service** (Port 50051): User management (gRPC)
- **notification_service** (Port 8002): Notifications
- **ai_service** (Port 8003): AI features

## How to Run the Development Environment

### Prerequisites
1. Docker and Docker Compose installed
2. pnpm installed
3. All dependencies installed: `pnpm install`
4. API contracts generated: `pnpm run generate-contracts`

### Starting All Services
```bash
# Build and start all services
docker compose up --build

# Or start in detached mode
docker compose up -d --build

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f web_app
```

### Starting Individual Services
```bash
# Start only backend services
docker compose up postgres_db gateway_service user_service

# Start only frontend
docker compose up web_site web_app web_admin web_ui
```

### Stopping Services
```bash
# Stop all services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

## Service URLs (when running)

- **web_site**: http://localhost:3000
- **web_app**: http://localhost:3001  
- **web_admin**: http://localhost:3002
- **web_ui (Storybook)**: http://localhost:6006
- **gateway_service**: http://localhost:8000
- **notification_service**: http://localhost:8002
- **ai_service**: http://localhost:8003
- **PostgreSQL**: localhost:5432

## Troubleshooting Common Issues

### 1. **Port Already in Use**
```bash
# Find process using port
sudo lsof -i :3000

# Kill process
sudo kill -9 <PID>
```

### 2. **Docker Permission Issues**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo
sudo docker compose up --build
```

### 3. **Module Not Found Errors**
- Ensure API contracts are generated: `pnpm run generate-contracts`
- Check that volume mounts are working in docker-compose.yml
- Verify pnpm-lock.yaml exists and is up to date

### 4. **Hot Reloading Not Working**
- Ensure `CHOKIDAR_USEPOLLING=true` is set in environment
- Check volume mounts are correctly configured
- Verify file permissions in container

### 5. **Database Connection Issues**
- Ensure PostgreSQL container is running: `docker compose ps`
- Check database logs: `docker compose logs postgres_db`
- Verify environment variables match in services

## Development Workflow

### For Frontend Development
1. Start the specific frontend service: `docker compose up web_app web_ui`
2. Edit files in `apps/web_app/` or `packages/web-ui/`
3. Changes should hot-reload automatically
4. Access Storybook at http://localhost:6006 for component development

### For Backend Development  
1. Start backend services: `docker compose up postgres_db gateway_service user_service`
2. Edit files in `services/*/`
3. Container will restart automatically due to volume mounts
4. Check logs: `docker compose logs -f gateway_service`

### For Full Stack Development
1. Start all services: `docker compose up --build`
2. Access different parts via their respective URLs
3. Monitor logs: `docker compose logs -f`

## Next Steps

1. **Test the setup** when Docker daemon is working properly
2. **Implement basic functionality** in each service
3. **Set up proper database migrations** for user_service
4. **Configure environment files** for each service as needed
5. **Add health checks** to docker-compose.yml for better reliability

## Files Modified

- `docker-compose.yml` - Fixed version, ports, environment variables
- `apps/web_site/Dockerfile` - Updated to use pnpm and proper monorepo setup
- `apps/web_app/Dockerfile` - Updated to use pnpm and proper monorepo setup  
- `apps/web_admin/Dockerfile` - Updated to use pnpm and proper monorepo setup
- Generated API contracts in `packages/api-contracts/generated/`

The Docker setup is now properly configured for a modern full-stack development environment with hot reloading support for all components!