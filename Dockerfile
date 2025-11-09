# Builder stage for any preparation steps
FROM python:3.9-slim AS builder

WORKDIR /app

# Install necessary build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Copy application files
# This assumes your code is in the build context
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/data

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Install runtime dependencies in a single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    ffmpeg \
    gcc \
    git \
    awscli \
    libgl1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1-mesa-dev \
    nano \
    wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application files from builder stage
COPY --from=builder /app/requirements.txt /app/
COPY --from=builder /app/src /app/src
COPY --from=builder /app/data /app/data

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir pycocotools && \
    pip3 install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose application port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]
