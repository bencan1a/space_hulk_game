# Space Hulk Game - Backend API

Browser-based game creation and play interface backend built with FastAPI.

## Features

- **FastAPI Application**: Modern async Python web framework
- **Health Check Endpoint**: Monitor application status at `/health`
- **OpenAPI Documentation**: Interactive API docs at `/docs` and `/redoc`
- **Configuration Management**: Environment-based config with Pydantic Settings
- **Structured Logging**: JSON-formatted logs with timestamps
- **CORS Support**: Configured for frontend integration
- **Type Safety**: Full type hints with mypy validation
- **Code Quality**: Enforced with ruff linting

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app initialization
│   ├── config.py         # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   └── models/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── test_health.py
│   └── test_config.py
├── .env.example
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Setup

### Prerequisites

- Python 3.10+
- pip or uv package manager

### Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. Create environment file:
   ```bash
   cp .env.example .env
   ```

4. (Optional) Edit `.env` to customize configuration

## Running the Server

### Development Mode

Start the server with auto-reload:

```bash
uvicorn app.main:app --reload
```

Or with custom host/port:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **OpenAPI Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Production Mode

For production deployment:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Development

### Code Quality

Run linting:
```bash
ruff check .
```

Auto-fix linting issues:
```bash
ruff check . --fix
```

Format code:
```bash
ruff format .
```

Type checking:
```bash
mypy . --strict
```

### Testing

Run all tests:
```bash
pytest -v
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_health.py -v
```

### Running All Checks

```bash
# Lint
ruff check .

# Format check
ruff format --check .

# Type check
mypy . --strict

# Tests
pytest -v
```

## Configuration

Configuration is managed through environment variables using Pydantic Settings.

### Environment Variables

See `.env.example` for all available configuration options:

- `API_HOST`: Host to bind the server (default: 0.0.0.0)
- `API_PORT`: Port to bind the server (default: 8000)
- `API_ENVIRONMENT`: Environment name (development, staging, production)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `CORS_ORIGINS`: Allowed CORS origins as JSON array
- `DATABASE_URL`: Database connection string (placeholder)

### Accessing Configuration

```python
from app.config import settings

print(settings.api_port)  # 8000
print(settings.log_level)  # INFO
```

## API Endpoints

### Health Check

**GET** `/health`

Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-13T12:00:00.000000Z"
}
```

## Logging

The application uses structured JSON logging:

```json
{
  "timestamp": "2025-11-13 12:00:00,000",
  "level": "INFO",
  "module": "main",
  "message": "Starting Space Hulk Game API"
}
```

Log level can be configured via the `LOG_LEVEL` environment variable.

## Next Steps

This is the foundation backend setup (Task 1.1). Future tasks will add:

- Database integration with SQLAlchemy and Alembic
- Story management endpoints
- Game session management
- WebSocket support for real-time updates
- Integration with CrewAI agents
- Authentication and authorization

## Support

For issues or questions, refer to the main project documentation or create an issue in the repository.
