#!/bin/bash
set -e

# Fix ownership of mounted volumes (runs as root initially)
chown -R appuser:appgroup /app/data 2>/dev/null || true

# Run database migrations as appuser
echo "Running database migrations..."
gosu appuser alembic upgrade head

# Execute the main command as appuser
echo "Starting application..."
exec gosu appuser "$@"
