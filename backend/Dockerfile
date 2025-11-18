FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1000 appuser

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies (with trusted host for network restrictions)
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
    -r requirements.txt -r requirements-dev.txt

# Copy application code and entrypoint
COPY . .
COPY entrypoint.sh /entrypoint.sh

# Make entrypoint executable and create data directory
RUN chmod +x /entrypoint.sh && \
    mkdir -p /app/data && \
    chown -R appuser:appgroup /app

# Expose port
EXPOSE 8000

# Use entrypoint that handles permissions and drops to appuser
ENTRYPOINT ["/entrypoint.sh"]

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
