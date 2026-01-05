FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV, PDF processing, and zbar (pyzbar)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glvnd \
    poppler-utils \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir fastapi uvicorn

# Copy application code
COPY src/ ./src/
COPY qr_client.py .
COPY api_server.py .

# Use PORT env variable (set by Cloud Run/Render)
ENV PORT=8080

# Run the HTTP API server
CMD exec python api_server.py
