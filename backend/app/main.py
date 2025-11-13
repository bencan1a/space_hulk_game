"""FastAPI application initialization and configuration."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings

# Setup structured logging
logging.basicConfig(
    level=settings.log_level,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Handle application startup and shutdown.

    Args:
        _app: FastAPI application instance (unused but required by interface)

    Yields:
        None
    """
    logger.info("Starting Space Hulk Game API", extra={"version": "1.0.0"})
    yield
    logger.info("Shutting down Space Hulk Game API")


app = FastAPI(
    title="Space Hulk Game API",
    description="Browser-based game creation and play interface",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        dict: Health status, version, and timestamp

    Example:
        >>> response = await health_check()
        >>> assert response["status"] == "healthy"
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
