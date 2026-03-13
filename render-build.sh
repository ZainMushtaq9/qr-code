#!/usr/bin/env bash
# Render Build Script — installs system deps + Python packages

set -o errexit

# Install system library needed by pyzbar
apt-get update && apt-get install -y libzbar0

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
