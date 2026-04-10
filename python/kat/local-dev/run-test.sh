#!/usr/bin/env bash
set -e

# Run a single KAT test locally
# Usage: ./run-test.sh <TestName>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
cd "$REPO_ROOT"

if [ -z "$1" ]; then
    echo "Usage: $0 <TestName>"
    echo ""
    echo "Available tests can be found in python/tests/kat/t_*.py files"
    echo ""
    echo "Examples:"
    echo "  $0 Empty"
    echo "  $0 AmbassadorIDTest"
    echo "  $0 CORS"
    echo "  $0 TLS"
    echo ""
    echo "Note: Run ./setup-environment.sh first if you haven't already"
    exit 1
fi

TEST_NAME="$1"

# Check if k3d cluster exists
if ! tools/bin/k3d cluster list 2>/dev/null | grep -q k3s-default; then
    echo "Error: k3d cluster not found"
    echo "Please run ./setup-environment.sh first"
    exit 1
fi

# Detect architecture
ARCH="$(uname -m)"
if [ "$ARCH" = "arm64" ]; then
    BUILD_ARCH="linux/arm64"
else
    BUILD_ARCH="linux/amd64"
fi

# Set environment variables
export SKIP_BASE_PYTHON_PUSH=1
export BUILD_ARCH="$BUILD_ARCH"
export ENVOY_DOCKER_REPO=docker.io/emissaryingress/base-envoy
export DEV_KUBECONFIG=~/.kube/config
export DEV_REGISTRY=localhost:5000
export VERSION=v0.0.0-test
export PYTEST_ARGS="-p no:nose -k $TEST_NAME python/tests/kat"

# Make sure we're using the right kubectl context
tools/bin/kubectl config use-context k3d-k3s-default >/dev/null 2>&1 || true

echo "========================================="
echo "Running KAT Test: $TEST_NAME"
echo "========================================="
echo "Architecture: $BUILD_ARCH"
echo "Registry: $DEV_REGISTRY"
echo "========================================="
echo ""

# Ensure local registry is running
echo "Checking local registry..."
if ! docker ps --format '{{.Names}}' | grep -q "emissary-registry"; then
    echo "Local registry not running. Starting it..."
    "$SCRIPT_DIR/setup-registry.sh" | tail -3
    docker network connect k3d-k3s-default emissary-registry 2>/dev/null || true
fi
echo "✓ Registry ready"
echo ""

# Build and push images to local registry
echo "Building and pushing images to local registry..."
make push-pytest-images 2>&1 | grep -E "(Pushing|digest:|DONE)" | tail -5
echo "✓ Images built and pushed"
echo ""

# Import images into k3d
echo "Importing images into k3d..."
for img in emissary kat-client kat-server test-auth test-shadow test-stats; do
    tools/bin/k3d image import localhost:5000/$img:0.0.0-test --cluster k3s-default 2>&1 | grep -E "Successfully" || true
done
echo "✓ Images imported"
echo ""

# Run the test
echo "Running test..."
echo ""
make pytest
