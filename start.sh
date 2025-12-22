#!/bin/bash
set -e

# Get port from environment or default to 8000
PORT=${PORT:-8000}

echo "Starting QR Code Scanner API on port $PORT..."
exec python api_server.py
