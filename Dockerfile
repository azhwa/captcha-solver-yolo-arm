# Dockerfile for ARM64 platforms - Debian Bookworm (Stable)
# Use this if you encounter package compatibility issues with the default Dockerfile
# Compatible with: ARM64 VPS, AWS Graviton, Oracle ARM, Raspberry Pi 4/5, Apple Silicon M1/M2

# Use Python 3.11 slim on Debian Bookworm (stable)
FROM --platform=linux/arm64 python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and ARM optimization
# Bookworm still uses libgl1-mesa-glx (more compatible)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    libopenblas-dev \
    liblapack-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies with ARM64 optimizations
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the model file
COPY best.pt /app/best.pt

# Copy the API code
COPY api /app/api

# Create temp results directory
RUN mkdir -p /app/temp_results

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=/app/best.pt
ENV OMP_NUM_THREADS=4
ENV OPENBLAS_NUM_THREADS=4

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
