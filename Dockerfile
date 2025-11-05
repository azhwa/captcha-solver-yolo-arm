# Multi-stage Dockerfile for ARM64 platforms - Optimized for Ampere VPS
# Stage 1: Builder - Compile dependencies
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

# Install build dependencies for compiling Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and create virtual environment
COPY requirements.txt .
RUN python -m venv /build/venv && \
    /build/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /build/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime - Minimal image with only runtime dependencies
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    libopenblas-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python virtual environment from builder
COPY --from=builder /build/venv /app/venv

# Copy application code
COPY api /app/api

# Create necessary directories with proper permissions
RUN mkdir -p /app/temp_results /app/models /app/database && \
    chmod -R 755 /app/temp_results /app/models /app/database

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PATH="/app/venv/bin:$PATH" \
    MODEL_PATH=/app/best.pt \
    OMP_NUM_THREADS=4 \
    OPENBLAS_NUM_THREADS=4

# Healthcheck (increased start period for model loading)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run application
CMD ["/app/venv/bin/python", "-m", "uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
