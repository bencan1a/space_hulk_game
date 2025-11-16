"""WebSocket endpoints for real-time progress updates.

This module provides WebSocket support for streaming progress updates
from story generation tasks to connected clients.
"""

import asyncio
import logging
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections for real-time progress updates.

    This manager tracks active WebSocket connections for each session,
    allowing broadcast of progress messages to all clients connected
    to a specific session.
    """

    def __init__(self) -> None:
        """Initialize the connection manager."""
        # Map of session_id -> list of active WebSocket connections
        self.active_connections: dict[str, list[WebSocket]] = {}
        self._heartbeat_interval: int = 30  # seconds

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """Accept a new WebSocket connection and register it.

        Args:
            websocket: The WebSocket connection to accept
            session_id: The session ID this connection is for
        """
        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        self.active_connections[session_id].append(websocket)

        logger.info(
            f"WebSocket connected for session {session_id}. "
            f"Total connections: {len(self.active_connections[session_id])}"
        )

        # Send initial connection confirmation
        await self._send_to_websocket(
            websocket,
            {
                "type": "connection",
                "status": "connected",
                "session_id": session_id,
            },
        )

    def disconnect(self, websocket: WebSocket, session_id: str) -> None:
        """Remove a WebSocket connection.

        Args:
            websocket: The WebSocket connection to remove
            session_id: The session ID this connection was for
        """
        if session_id in self.active_connections and websocket in self.active_connections[session_id]:
            self.active_connections[session_id].remove(websocket)

            logger.info(
                f"WebSocket disconnected for session {session_id}. "
                f"Remaining connections: {len(self.active_connections[session_id])}"
            )

            # Clean up empty session lists
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
                logger.info(f"Removed session {session_id} from active connections")

    async def broadcast_to_session(self, session_id: str, message: dict[str, Any]) -> None:
        """Broadcast a message to all connections for a specific session.

        Args:
            session_id: The session ID to broadcast to
            message: The message to broadcast (will be JSON-encoded)
        """
        if session_id not in self.active_connections:
            logger.debug(f"No active connections for session {session_id}")
            return

        # Get connections to send to (copy to avoid modification during iteration)
        connections = self.active_connections[session_id].copy()

        if not connections:
            logger.debug(f"No active connections for session {session_id}")
            return

        logger.info(
            f"Broadcasting to {len(connections)} connection(s) for session {session_id}: "
            f"{message.get('type', 'unknown')}"
        )

        # Send to all connections
        disconnected: list[WebSocket] = []

        for connection in connections:
            try:
                await self._send_to_websocket(connection, message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.append(connection)

        # Clean up any disconnected connections
        for connection in disconnected:
            self.disconnect(connection, session_id)

    async def _send_to_websocket(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        """Send a JSON message to a single WebSocket.

        Args:
            websocket: The WebSocket to send to
            message: The message to send (will be JSON-encoded)

        Raises:
            Exception: If sending fails (connection closed, etc.)
        """
        await websocket.send_json(message)

    async def send_heartbeat(self, websocket: WebSocket, session_id: str) -> None:
        """Send periodic heartbeat messages to keep connection alive.

        Args:
            websocket: The WebSocket to send heartbeat to
            session_id: The session ID for this connection
        """
        try:
            while True:
                await asyncio.sleep(self._heartbeat_interval)

                # Check if connection is still active
                if session_id not in self.active_connections:
                    break

                if websocket not in self.active_connections[session_id]:
                    break

                # Send heartbeat ping
                await self._send_to_websocket(
                    websocket,
                    {
                        "type": "heartbeat",
                        "session_id": session_id,
                    },
                )

                logger.debug(f"Sent heartbeat to session {session_id}")

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected during heartbeat for session {session_id}")
        except Exception as e:
            logger.error(f"Error in heartbeat for session {session_id}: {e}")
        finally:
            self.disconnect(websocket, session_id)

    def get_connection_count(self, session_id: str | None = None) -> int:
        """Get the number of active connections.

        Args:
            session_id: If provided, get count for specific session.
                       If None, get total count across all sessions.

        Returns:
            Number of active connections
        """
        if session_id is not None:
            return len(self.active_connections.get(session_id, []))

        return sum(len(conns) for conns in self.active_connections.values())


# Global connection manager instance
manager = ConnectionManager()


def broadcast_progress(session_id: str, status: str, data: dict[str, Any]) -> None:
    """Broadcast a progress update to all WebSocket clients for a session.

    This function is designed to be called from the progress_callback in
    generation_tasks.py. It runs the async broadcast in a safe way that
    works from synchronous contexts.

    Args:
        session_id: The session ID to broadcast to
        status: The progress status type (e.g., "started", "task_completed")
        data: Additional data to include in the message
    """
    message = {
        "type": "progress",
        "status": status,
        "session_id": session_id,
        **data,
    }

    # Create an event loop if one doesn't exist, or use existing one
    try:
        loop = asyncio.get_running_loop()
        # If loop is running, schedule the coroutine
        # Note: We don't store the task reference since it's fire-and-forget
        # and will be cleaned up automatically
        _ = asyncio.create_task(manager.broadcast_to_session(session_id, message))  # noqa: RUF006
    except RuntimeError:
        # No event loop in current thread, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(manager.broadcast_to_session(session_id, message))
        finally:
            loop.close()
