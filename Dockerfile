# Dockerfile for Gauge Test Environment
# Minimal setup for testing gauge widgets

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Note: Application files are NOT copied here
# They will be mounted as volumes from the host directory
# This allows hot-reload during development without rebuilding the image

# Expose test port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden in docker-compose)
# Background images will be generated on first run if PIL is available
CMD ["python3", "test_apps/test_both_gauges.py"]

