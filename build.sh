#!/bin/bash
set -e

# Install system dependencies for OpenCV and graphics libraries
apt-get update
apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libpoppler-cpp0

# Install Python dependencies
pip install -r requirements-cloud.txt
