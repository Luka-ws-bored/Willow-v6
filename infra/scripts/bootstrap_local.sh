#!/bin/bash

# Bootstrap script for local development environment
# This script sets up the local development environment for Willow

echo "Starting local development environment bootstrap..."

# Check if docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed or not in PATH"
    exit 1
fi

# Start the services
echo "Starting Ollama and Chroma services..."
docker-compose -f infra/docker-compose.local.yml up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check if services are running
echo "Checking service status..."
docker-compose -f infra/docker-compose.local.yml ps

echo "Bootstrap complete!"
echo "Ollama should be available at http://localhost:11434"
echo "Chroma should be available at http://localhost:8000"