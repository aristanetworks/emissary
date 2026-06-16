#!/usr/bin/env bash
set -e

# One-time setup for running KAT tests locally
# This script:
# 1. Sets up a local Docker registry
# 2. Creates a k3d Kubernetes cluster
# 3. Builds Emissary images
# 4. Sets up Python venv

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
cd "$REPO_ROOT"

echo "========================================="
echo "KAT Local Development Setup"
echo "========================================="
echo ""

# Detect architecture
ARCH="$(uname -m)"
if [ "$ARCH" = "arm64" ]; then
    BUILD_ARCH="linux/arm64"
    echo "Detected: ARM64 (Apple Silicon)"
else
    BUILD_ARCH="linux/amd64"
    echo "Detected: AMD64 (Intel)"
fi

# Set environment variables
export SKIP_BASE_PYTHON_PUSH=1
export BUILD_ARCH="$BUILD_ARCH"
export ENVOY_DOCKER_REPO=docker.io/emissaryingress/base-envoy
export DEV_REGISTRY=localhost:5000

echo ""

# Step 1: Set up local Docker registry
echo "Step 1: Setting up local Docker registry..."
"$SCRIPT_DIR/setup-registry.sh" | grep -E "✓|Registry:"
echo ""

# Step 2: Create or verify k3d cluster
echo "Step 2: Setting up k3d cluster..."
if tools/bin/k3d cluster list 2>/dev/null | grep -q k3s-default; then
    echo "✓ k3d cluster already exists"
    # Ensure registry is connected to k3d network
    docker network connect k3d-k3s-default emissary-registry 2>/dev/null || \
        echo "  (registry already connected)"
else
    echo "Creating k3d cluster..."
    make ci/setup-k3d
    # Connect registry to k3d network
    docker network connect k3d-k3s-default emissary-registry
    echo "✓ k3d cluster created"
fi

# Configure kubectl
export DEV_KUBECONFIG=~/.kube/config
tools/bin/kubectl config use-context k3d-k3s-default 2>/dev/null || true
echo ""

# Step 3: Build images
echo "Step 3: Building Emissary images..."
echo "This may take 30-60 minutes on first run..."
echo ""
if make images; then
    echo ""
    echo "✓ Images built successfully"
else
    echo ""
    echo "✗ Image build failed"
    echo ""
    echo "Common issues:"
    echo "  - Missing Envoy image: Run ./get-envoy-image.sh"
    echo "  - Docker not running: Start Docker Desktop"
    echo "  - Insufficient disk space: Need ~10GB free"
    exit 1
fi
echo ""

# Step 4: Set up Python test environment
echo "Step 4: Setting up Python test environment..."
if [ ! -d "venv" ]; then
    make python-dev-setup
    echo "✓ Python venv created"
else
    echo "✓ Python venv already exists"
fi
echo ""

echo "========================================="
echo "Setup Complete! 🎉"
echo "========================================="
echo ""
echo "You can now run KAT tests:"
echo "  cd python/kat/local-dev"
echo "  ./run-test.sh <TestName>"
echo ""
echo "Examples:"
echo "  ./run-test.sh Empty"
echo "  ./run-test.sh AmbassadorIDTest"
echo ""
echo "To cleanup later:"
echo "  make ci/teardown-k3d"
echo "  docker stop emissary-registry"
echo ""
