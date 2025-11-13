#!/bin/bash
set -e

echo "Testing Docker Compose setup..."

# Start services
echo "Starting services..."
docker compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
docker compose wait backend frontend || exit 1

# Test backend health
echo "Testing backend health endpoint..."
curl -f http://localhost:8000/health || exit 1

# Test frontend
echo "Testing frontend..."
curl -f http://localhost:3000 || exit 1

# Test Redis connection
echo "Testing Redis..."
docker compose exec -T redis redis-cli ping | grep -q "PONG" || exit 1

# Check service logs for errors
echo "Checking for errors in logs..."
docker compose logs backend | grep -i "error" && exit 1 || true
docker compose logs frontend | grep -i "error" && exit 1 || true

# Test backend-redis communication
echo "Testing backend-redis communication..."
docker compose exec -T backend python -c "import redis; r = redis.from_url('redis://redis:6379/0'); r.ping()" || exit 1

echo "All tests passed!"

# Stop services
docker compose down
