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
check_url "http://localhost:8002" "notification_service"
check_url "http://localhost:8003" "ai_service"

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
echo "# Stop all services:"
echo "docker compose down"
echo ""

echo "Health check complete! 🏁"