# Docker Setup Guide

This guide explains how to run the Space Hulk Game using Docker Compose for local development.

## Prerequisites

- Docker (version 20.10 or later)
- Docker Compose V2 (comes with Docker Desktop)
- At least 4GB of RAM available for Docker
- At least 5GB of free disk space

## Quick Start

### 1. Copy Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` if needed to customize any configuration values.

### 2. Start All Services

```bash
docker compose up --build
```

This will:
- Build the frontend (React + Vite) container
- Build the backend (FastAPI) container
- Pull Redis image
- Start all services with live reload enabled

### 3. Access the Application

Once all services are running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Redis**: localhost:6379 (internal only)

## Available Services

### Frontend Service
- **Framework**: React with TypeScript + Vite
- **Port**: 3000
- **Hot Reload**: Enabled (changes to `frontend/src` will auto-reload)
- **Environment**: Development mode

### Backend Service
- **Framework**: FastAPI with Python 3.11
- **Port**: 8000
- **Hot Reload**: Enabled (changes to `backend/app` will auto-reload)
- **Database**: SQLite at `./data/database.db`
- **Environment**: Development mode

### Celery Worker Service
- **Purpose**: Asynchronous task processing
- **Broker**: Redis
- **Auto-restart**: Yes
- **Log Level**: INFO

### Redis Service
- **Version**: 7-alpine
- **Port**: 6379 (exposed for debugging)
- **Health Check**: Enabled
- **Data Persistence**: No (development mode)

## Common Commands

### Start Services (Detached Mode)
```bash
docker compose up -d
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f celery-worker
docker compose logs -f redis
```

### Stop Services
```bash
docker compose down
```

### Rebuild and Restart
```bash
docker compose up --build
```

### Remove Everything (including volumes)
```bash
docker compose down -v
```

### Check Service Status
```bash
docker compose ps
```

### Execute Commands in Containers
```bash
# Backend shell
docker compose exec backend bash

# Run backend tests
docker compose exec backend python -m unittest discover -s tests -v

# Frontend shell
docker compose exec frontend sh

# Redis CLI
docker compose exec redis redis-cli
```

## Development Workflow

### 1. Code Changes with Hot Reload

**Backend Changes:**
1. Edit files in `backend/app/`
2. Uvicorn automatically detects changes and reloads
3. Check logs: `docker compose logs -f backend`

**Frontend Changes:**
1. Edit files in `frontend/src/`
2. Vite automatically detects changes and hot-reloads
3. Browser will update automatically

### 2. Adding Dependencies

**Backend (Python):**
1. Add package to `backend/requirements.txt`
2. Rebuild: `docker compose up --build backend`

**Frontend (npm):**
1. Add package to `frontend/package.json`
2. Rebuild: `docker compose up --build frontend`

### 3. Database Changes

The SQLite database is stored in `./data/database.db` and persists across container restarts.

To reset the database:
```bash
docker compose down
rm -f ./data/database.db
docker compose up
```

## Testing the Setup

Run the automated test script:

```bash
chmod +x test_docker_setup.sh
./test_docker_setup.sh
```

This script:
- Starts all services
- Waits for them to be ready
- Tests backend health endpoint
- Tests frontend accessibility
- Tests Redis connection
- Tests backend-Redis communication
- Checks logs for errors
- Stops all services

## Troubleshooting

### Port Already in Use

If you get "port is already allocated" errors:

```bash
# Find what's using the port
lsof -i :3000  # or :8000, :6379

# Stop the conflicting service or change ports in docker-compose.yml
```

### Container Won't Start

```bash
# View logs for the failing service
docker compose logs <service-name>

# Remove all containers and start fresh
docker compose down -v
docker compose up --build
```

### Changes Not Reflecting

```bash
# For backend: ensure volume mount is correct
docker compose down
docker compose up --build backend

# For frontend: clear Vite cache
docker compose exec frontend rm -rf node_modules/.vite
docker compose restart frontend
```

### Out of Disk Space

```bash
# Clean up Docker resources
docker system prune -a

# Remove unused volumes
docker volume prune
```

### Network Issues

If services can't communicate:

```bash
# Recreate the network
docker compose down
docker network prune
docker compose up
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Host Machine                       │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐                │
│  │   Browser    │  │   curl/tools │                │
│  └──────┬───────┘  └──────┬───────┘                │
│         │                  │                        │
│         │ :3000      :8000 │                        │
├─────────┼──────────────────┼────────────────────────┤
│         │                  │                        │
│  ┌──────▼───────┐  ┌──────▼──────┐                 │
│  │   Frontend   │  │   Backend   │                 │
│  │  (React +    │  │  (FastAPI)  │                 │
│  │   Vite)      │  │             │                 │
│  └──────────────┘  └──────┬──────┘                 │
│                            │                        │
│         ┌──────────────────┼─────────┐              │
│         │                  │         │              │
│  ┌──────▼──────┐  ┌───────▼───────┐ │              │
│  │   Celery    │  │     Redis     │ │              │
│  │   Worker    │  │   (Broker)    │ │              │
│  └─────────────┘  └───────────────┘ │              │
│                                      │              │
│  ┌──────────────────────────────────▼──┐           │
│  │      SQLite Database                │           │
│  │      (./data/database.db)           │           │
│  └─────────────────────────────────────┘           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Production Deployment

For production deployment, use `docker-compose.prod.yml` (currently a placeholder).

Key differences for production:
- Remove volume mounts (no hot reload)
- Use production builds
- Switch to PostgreSQL
- Add nginx reverse proxy
- Enable SSL/TLS
- Set resource limits
- Use secrets for environment variables
- Enable restart policies

## Environment Variables

See `.env.example` for all available configuration options.

Key variables for Docker:
- `API_HOST` - Backend bind address (default: 0.0.0.0)
- `API_PORT` - Backend port (default: 8000)
- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis connection string
- `VITE_API_URL` - Frontend API endpoint
- `LOG_LEVEL` - Logging verbosity (DEBUG, INFO, WARNING, ERROR)

## Security Notes

⚠️ **Development Only**: This Docker Compose configuration is for local development only.

For production:
- Use secrets for sensitive environment variables
- Don't expose Redis port
- Use PostgreSQL with authentication
- Enable HTTPS/TLS
- Set up proper CORS policies
- Use non-root users in containers
- Scan images for vulnerabilities

## Performance Tips

1. **Use BuildKit** (enabled by default in Docker 20.10+)
2. **Layer Caching**: Order Dockerfile commands from least to most frequently changing
3. **Multi-stage Builds**: Consider for production builds
4. **Resource Limits**: Add in docker-compose.yml if needed:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

## Support

For issues or questions:
1. Check the logs: `docker compose logs -f`
2. Review this guide
3. Check GitHub issues
4. Refer to main README.md

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite Documentation](https://vitejs.dev/)
- [Celery Documentation](https://docs.celeryproject.org/)
