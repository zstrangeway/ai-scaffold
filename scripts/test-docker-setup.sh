#!/bin/bash

# Docker Setup Health Check Script
# This script tests that all services are running and accessible

echo "🔍 Testing Docker Compose Setup..."

# Function to check if a URL responds
check_url() {
    local url=$1
    local service=$2
    echo -n "Testing $service ($url)... "
    
    if curl -s --max-time 10 "$url" > /dev/null 2>&1; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAILED"
        return 1
    fi
}

# Function to check if a port is open
check_port() {
    local port=$1
    local service=$2
    echo -n "Testing $service (port $port)... "
    
    if nc -z localhost "$port" 2>/dev/null; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAILED"
        return 1
    fi
}

echo ""
echo "📋 Checking Docker Compose services..."
docker compose ps

echo ""
echo "🌐 Testing HTTP Services..."

# Test frontend services
check_url "http://localhost:3000" "web_site"
check_url "http://localhost:3001" "web_app" 
check_url "http://localhost:3002" "web_admin"
check_url "http://localhost:6006" "web_ui (Storybook)"

# Test backend services
check_url "http://localhost:8000" "gateway_service"
check_url "http://localhost:8000/health" "gateway_service health"
check_url "http://localhost:8002" "notification_service"
check_url "http://localhost:8002/health" "notification_service health"
check_url "http://localhost:8003" "ai_service"
check_url "http://localhost:8003/health" "ai_service health"

echo ""
echo "🔌 Testing Database and gRPC Services..."

# Test database
check_port 5432 "PostgreSQL"

# Test gRPC service
check_port 50051 "user_service (gRPC)"

echo ""
echo "📦 Checking Generated API Contracts..."
if [ -d "packages/api-contracts/generated/ts" ] && [ -d "packages/api-contracts/generated/py" ]; then
    echo "✅ API contracts generated successfully"
    
    # Check specific files
    if [ -f "packages/api-contracts/generated/py/user_service_pb2.py" ]; then
        echo "✅ Python gRPC stubs available"
    else
        echo "❌ Python gRPC stubs missing"
    fi
    
    if [ -f "packages/api-contracts/generated/ts/user_service_pb.ts" ]; then
        echo "✅ TypeScript protobuf definitions available"
    else
        echo "❌ TypeScript protobuf definitions missing"
    fi
else
    echo "❌ API contracts missing - run 'pnpm run generate-contracts'"
fi

echo ""
echo "🧹 Checking for Common Issues..."

# Check for package-lock.json files (should use pnpm-lock.yaml)
if find . -name "package-lock.json" -not -path "./node_modules/*" | grep -q .; then
    echo "⚠️  Warning: Found package-lock.json files. Remove them and use pnpm-lock.yaml"
    find . -name "package-lock.json" -not -path "./node_modules/*"
else
    echo "✅ No conflicting package-lock.json files"
fi

# Check if pnpm-lock.yaml exists
if [ -f "pnpm-lock.yaml" ]; then
    echo "✅ pnpm-lock.yaml exists"
else
    echo "❌ pnpm-lock.yaml missing - run 'pnpm install'"
fi

# Check Python dependencies
echo ""
echo "🐍 Checking Python Service Dependencies..."

if [ -f "services/user_service/poetry.lock" ]; then
    echo "✅ user_service dependencies locked"
else
    echo "❌ user_service poetry.lock missing"
fi

if [ -f "services/gateway_service/poetry.lock" ]; then
    echo "✅ gateway_service dependencies locked"
else
    echo "❌ gateway_service poetry.lock missing"
fi

# Check for protobuf version compatibility
echo ""
echo "📋 Checking Configuration..."

if grep -q 'protobuf = "\^4\.25\.0"' services/*/pyproject.toml; then
    echo "✅ Compatible protobuf versions configured"
else
    echo "⚠️  Warning: Check protobuf versions in pyproject.toml files"
fi

# Check Docker Compose setup
if grep -q "CHOKIDAR_USEPOLLING=true" docker-compose.yml; then
    echo "✅ Hot reloading configured"
else
    echo "❌ Hot reloading not configured"
fi

echo ""
echo "🎯 Quick Commands for Development:"
echo ""
echo "# Start all services:"
echo "docker compose up --build"
echo ""
echo "# Start only frontend:"
echo "docker compose up web_site web_app web_admin web_ui"
echo ""
echo "# Start only backend:"
echo "docker compose up postgres_db gateway_service user_service notification_service ai_service"
echo ""
echo "# View logs:"
echo "docker compose logs -f"
echo ""
echo "# View specific service logs:"
echo "docker compose logs -f gateway_service"
echo ""
echo "# Rebuild specific service:"
echo "docker compose build --no-cache gateway_service"
echo ""
echo "# Clean restart (remove volumes):"
echo "docker compose down -v && docker compose up --build"
echo ""
echo "# Generate API contracts:"
echo "pnpm run generate-contracts"
echo ""
echo "# Stop all services:"
echo "docker compose down"
echo ""

echo "Health check complete! 🏁"

echo ""
echo "📚 For detailed troubleshooting, see: DOCKER_SETUP_FIXES.md"