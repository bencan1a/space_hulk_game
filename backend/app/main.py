"""FastAPI application initialization and configuration."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from celery.result import AsyncResult
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .api.routes import stories, templates, themes
from .api.websocket import manager as websocket_manager
from .celery_app import celery_app
from .config import settings
from .tasks.example_task import example_long_task

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
    logger.info("Starting Space Hulk Game API", extra={"version": __version__})
    yield
    logger.info("Shutting down Space Hulk Game API")


app = FastAPI(
    title="Space Hulk Game API",
    description="Browser-based game creation and play interface",
    version=__version__,
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

# Register routers
app.include_router(stories.router)
app.include_router(templates.router)
app.include_router(themes.router)


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
        "version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


@app.post("/api/v1/tasks/example")
async def trigger_example_task(
    duration: int = Query(default=10, ge=1, le=300, description="Task duration in seconds"),
) -> dict[str, str]:
    """
    Trigger an example long-running task.

    Args:
        duration: How long the task should run (seconds, 1-300)

    Returns:
        dict: Task ID for status checking
    """
    task = example_long_task.delay(duration)
    return {"task_id": task.id, "status": "started"}


@app.get("/api/v1/tasks/{task_id}/status")
async def get_task_status(task_id: str) -> dict[str, Any]:
    """
    Get status of a running task.

    Args:
        task_id: Celery task ID

    Returns:
        dict: Task status and result/progress
    """
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.state == "PENDING":
        response = {"state": task_result.state, "status": "Task is waiting to start"}
    elif task_result.state == "PROGRESS":
        info = task_result.info or {}
        response = {
            "state": task_result.state,
            "progress": info.get("progress", 0),
            "status": info.get("status", ""),
        }
    elif task_result.state == "SUCCESS":
        response = {"state": task_result.state, "result": task_result.result}
    elif task_result.state == "FAILURE":
        response = {"state": task_result.state, "error": str(task_result.info)}
    else:
        response = {"state": task_result.state, "status": "Unknown state"}

    return response


@app.websocket("/ws/progress/{session_id}")
async def websocket_progress_endpoint(websocket: WebSocket, session_id: str) -> None:
    """
    WebSocket endpoint for real-time progress updates.

    Clients connect to this endpoint to receive real-time progress updates
    for a specific generation session. The connection supports:
    - Automatic heartbeat messages every 30 seconds to keep connection alive
    - Progress messages broadcast from generation tasks
    - Graceful disconnection handling

    Args:
        websocket: The WebSocket connection
        session_id: The generation session ID to receive updates for

    Example:
        Connect via JavaScript:
        ```javascript
        const ws = new WebSocket('ws://localhost:8000/ws/progress/session-123');
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Progress:', data);
        };
        ```
    """
    await websocket_manager.connect(websocket, session_id)

    try:
        # Start heartbeat task
        heartbeat_task = asyncio.create_task(
            websocket_manager.send_heartbeat(websocket, session_id)
        )

        # Listen for client messages (mostly for connection management)
        while True:
            try:
                # Wait for any message from client
                data = await websocket.receive_text()
                logger.debug(f"Received message from client for session {session_id}: {data}")

                # Echo back acknowledgment (optional)
                # Client messages are primarily to keep connection alive
                # The main communication direction is server -> client

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for session {session_id}")
                break

    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")

    finally:
        # Cancel heartbeat task
        if "heartbeat_task" in locals():
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass

        # Disconnect
        websocket_manager.disconnect(websocket, session_id)
