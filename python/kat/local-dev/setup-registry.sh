#!/usr/bin/env bash
set -e

# Setup a local Docker registry for KAT testing
# This allows images to be "pushed" locally without going to a remote registry

REGISTRY_NAME="emissary-registry"
REGISTRY_PORT="5000"

# Check if registry already exists and is running
if docker ps --format '{{.Names}}' | grep -q "^${REGISTRY_NAME}$"; then
    echo "✓ Local registry already running at localhost:${REGISTRY_PORT}"
    exit 0
fi

# Check if registry exists but is stopped
if docker ps -a --format '{{.Names}}' | grep -q "^${REGISTRY_NAME}$"; then
    echo "Starting existing registry..."
    docker start "${REGISTRY_NAME}" >/dev/null
    echo "✓ Registry started at localhost:${REGISTRY_PORT}"
    exit 0
fi

# Create new registry
echo "Creating local Docker registry..."
docker run -d \
    --name "${REGISTRY_NAME}" \
    --restart=always \
    -p "${REGISTRY_PORT}:5000" \
    registry:2 >/dev/null

# Verify registry is working
sleep 2
if curl -s http://localhost:${REGISTRY_PORT}/v2/ | grep -q "{}"; then
    echo "✓ Registry created and running at localhost:${REGISTRY_PORT}"
else
    echo "✗ Registry not responding correctly"
    exit 1
fi
