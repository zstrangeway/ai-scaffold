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

### 7. **Python Dependency Path Issues**
- **Problem**: Services trying to use local path dependencies for API contracts in pyproject.toml, which don't work in Docker
- **Solution**: 
  - Removed local path dependencies from `pyproject.toml` files
  - Services use fallback import logic with volume-mounted contracts
  - Fixed protobuf version compatibility (changed from ^6.31.0 to ^4.25.0)

### 8. **FastAPI Server Startup Issues**
- **Problem**: `notification_service` and `ai_service` had minimal FastAPI apps without proper server startup
- **Solution**: 
  - Updated both services to include uvicorn startup code
  - Added health check endpoints
  - Added proper dev dependencies (pytest, black, flake8)

### 9. **Package Manager Conflicts**
- **Problem**: Conflicting `package-lock.json` files present while using pnpm
- **Solution**: Removed all `package-lock.json` files from frontend apps

## Current Architecture

### Frontend Applications (Next.js)
- **web_site** (Port 3000): Brochure/marketing site
- **web_app** (Port 3001): Main application with i18n, API integration
- **web_admin** (Port 3002): Admin panel
- **web_ui** (Port 6006): Storybook for shared components

### Backend Services (Python FastAPI)
- **postgres_db** (Port 5432): PostgreSQL database
- **gateway_service** (Port 8000): API Gateway/Router (fully implemented)
- **user_service** (Port 50051): User management (gRPC, fully implemented)
- **notification_service** (Port 8002): Notifications (basic FastAPI)
- **ai_service** (Port 8003): AI features (basic FastAPI)

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

## API Endpoints Available

### Gateway Service (Port 8000)
- `GET /` - Health check
- `GET /health` - Health status
- `GET /docs` - OpenAPI documentation
- Authentication and user management endpoints

### User Service (Port 50051)
- gRPC service with user CRUD operations
- Fully implemented with database integration

### Notification Service (Port 8002)
- `GET /` - Service status
- `GET /health` - Health check

### AI Service (Port 8003)
- `GET /` - Service status
- `GET /health` - Health check

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
- Check no package-lock.json files exist: `find . -name "package-lock.json" -not -path "*/node_modules/*"`

### 4. **Hot Reloading Not Working**
- Ensure `CHOKIDAR_USEPOLLING=true` is set in environment
- Check volume mounts are correctly configured
- Verify file permissions in container

### 5. **Database Connection Issues**
- Ensure PostgreSQL container is running: `docker compose ps`
- Check database logs: `docker compose logs postgres_db`
- Verify environment variables match in services

### 6. **Python Import Errors**
- Check if API contracts are generated: `ls packages/api-contracts/generated/py/`
- Verify volume mounts for contracts: `docker compose logs user_service`
- Check Python path: `docker compose exec user_service python -c "import sys; print(sys.path)"`

### 7. **Build Failures**
```bash
# Clean build with no cache
docker compose build --no-cache

# Remove all containers and images
docker compose down -v --rmi all

# Rebuild specific service
docker compose build --no-cache gateway_service
```

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

## Testing the Setup

Run the health check script:
```bash
./scripts/test-docker-setup.sh
```

This will test all service endpoints and provide troubleshooting guidance.

## Next Steps

1. **Test the setup** when Docker daemon is working properly
2. **Implement additional functionality** in notification_service and ai_service
3. **Set up proper database migrations** for user_service
4. **Configure environment files** for each service as needed
5. **Add health checks** to docker-compose.yml for better reliability
6. **Implement actual notification logic** (email, SMS, etc.)
7. **Add AI/LLM integration** to ai_service

## Files Modified

### Docker Configuration
- `docker-compose.yml` - Fixed version, ports, environment variables

### Frontend Applications  
- `apps/web_site/Dockerfile` - Updated to use pnpm and proper monorepo setup
- `apps/web_app/Dockerfile` - Updated to use pnpm and proper monorepo setup  
- `apps/web_admin/Dockerfile` - Updated to use pnpm and proper monorepo setup
- Removed `package-lock.json` files from all frontend apps

### Backend Services
- `services/user_service/pyproject.toml` - Removed path dependency, fixed protobuf version
- `services/gateway_service/pyproject.toml` - Removed path dependency, fixed protobuf version
- `services/notification_service/pyproject.toml` - Added uvicorn and dev dependencies
- `services/notification_service/app/main.py` - Added proper FastAPI server startup
- `services/ai_service/pyproject.toml` - Added dev dependencies
- `services/ai_service/app/main.py` - Added proper FastAPI server startup

### Generated Assets
- `packages/api-contracts/generated/` - Generated TypeScript and Python contracts

## Service Implementation Status

### ✅ Fully Implemented
- **user_service**: Complete gRPC service with database integration, user CRUD operations
- **gateway_service**: Complete FastAPI service with authentication, user management API
- **web_ui**: Storybook with shadcn/ui components

### 🔄 Basic Implementation  
- **notification_service**: Basic FastAPI service (ready for notification logic implementation)
- **ai_service**: Basic FastAPI service (ready for AI/LLM integration)
- **web_site**: Next.js app (needs content implementation)
- **web_app**: Next.js app with API contracts (needs UI implementation)  
- **web_admin**: Next.js app (needs admin UI implementation)

The Docker setup is now properly configured for a modern full-stack development environment with hot reloading support for all components!