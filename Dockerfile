FROM python:3.11-bullseye

WORKDIR /app

# Full base image already has most system deps
# Just add zbar and poppler explicitly
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libzbar0 \
    poppler-utils \
    && apt-get clean \
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
