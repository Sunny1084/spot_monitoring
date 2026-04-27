#!/bin/bash
# Jenkins Container Setup Script
# Run this to install dependencies in Jenkins container

echo "Installing Python 3, pip, and Docker CLI..."

apt-get update
apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    git \
    curl \
    wget

# Install Docker CLI (connect to host Docker daemon)
# This allows Jenkins to use Docker without installing full Docker engine
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add jenkins user to docker group
usermod -aG docker jenkins || true

echo "Dependencies installed successfully!"
echo "Run: docker --version"
echo "Run: python3 --version"
