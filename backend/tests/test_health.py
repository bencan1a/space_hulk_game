"""Tests for health check endpoint."""

import sys
from datetime import datetime
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint_returns_200() -> None:
    """Test health endpoint returns 200 status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_response_structure() -> None:
    """Test health response has correct structure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        data = response.json()

        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_timestamp_format() -> None:
    """Test timestamp is valid ISO 8601 format."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        data = response.json()

        # Should not raise exception
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
