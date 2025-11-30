# Multi-architecture Dockerfile for air_tweets
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .
COPY templates/ ./templates/

# Create config directory (config file will be mounted at runtime)
RUN mkdir -p /app/config

# Create directory for storage
RUN mkdir -p /data

# Set environment variable for config path (can be overridden)
ENV CONFIG_PATH=/app/config/config.ini

# Run the application
CMD ["python", "-u", "tweet.py"]
