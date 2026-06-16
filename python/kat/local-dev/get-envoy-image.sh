#!/usr/bin/env bash
set -e

# Get a compatible Envoy base image for local KAT testing

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Read the required version from _cxx/envoy.mk
ENVOY_COMMIT="628f5afc75a894a08504fa0f416269ec50c07bf9"
ENVOY_TAG="envoy-0.${ENVOY_COMMIT}.opt"
ENVOY_REPO="docker.io/emissaryingress/base-envoy"
FULL_TAG="${ENVOY_REPO}:${ENVOY_TAG}"

echo "========================================="
echo "Getting Envoy Base Image"
echo "========================================="
echo ""
echo "Required: ${ENVOY_TAG}"
echo ""

# Check if image already exists locally
if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "${FULL_TAG}"; then
    echo "✓ Envoy image already available locally"
    exit 0
fi

# Try to pull exact version from Docker Hub
echo "Attempting to pull from Docker Hub..."
if docker pull "${FULL_TAG}" 2>/dev/null; then
    echo "✓ Successfully pulled exact version"
    exit 0
fi
echo "✗ Exact version not available"
echo ""

# Try GCR (may require authentication)
GCR_TAG="gcr.io/datawire/ambassador-base:${ENVOY_TAG}"
echo "Attempting to pull from GCR..."
if docker pull "${GCR_TAG}" 2>/dev/null; then
    echo "✓ Pulled from GCR"
    docker tag "${GCR_TAG}" "${FULL_TAG}"
    echo "✓ Tagged as ${FULL_TAG}"
    exit 0
fi
echo "✗ Not available in GCR (authentication may be required)"
echo ""

# Offer fallback options
echo "========================================="
echo "Exact version not found. Options:"
echo "========================================="
echo ""
echo "1. Use a recent compatible version (recommended for local testing):"
echo "   This may work but could have minor compatibility issues."
echo ""
echo "2. Build Envoy yourself (takes 1-2 hours):"
echo "   cd $REPO_ROOT"
echo "   make build-envoy"
echo ""

# Auto-fallback option
FALLBACK_TAG="docker.io/emissaryingress/base-envoy:envoy-1.99c27c6cf5753adb0390d05992d6e5f248f85ab2.opt"

read -p "Pull a recent compatible version? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Pulling ${FALLBACK_TAG}..."
    if docker pull "${FALLBACK_TAG}"; then
        echo "✓ Pulled fallback image"
        echo "Tagging as ${FULL_TAG}..."
        docker tag "${FALLBACK_TAG}" "${FULL_TAG}"
        echo "✓ Done! You can now run ./setup-environment.sh"
        exit 0
    else
        echo "✗ Failed to pull fallback image"
        exit 1
    fi
fi

echo ""
echo "No Envoy image configured. Please choose one of the options above."
exit 1
