# Running KAT Tests Locally

This directory contains scripts and documentation for running KAT (Kubernetes Acceptance Tests) locally on your development machine.

## Quick Start

### Prerequisites
- Docker Desktop running
- ~10GB free disk space

### One-Time Setup

```bash
# 1. Get a compatible Envoy base image
./get-envoy-image.sh

# 2. Set up the local test environment (k3d cluster + local registry)
./setup-environment.sh
```

### Run a Single Test

```bash
./run-test.sh <TestName>
```

**Examples:**
```bash
./run-test.sh Empty
./run-test.sh AmbassadorIDTest
./run-test.sh CORS
./run-test.sh TLS
```

Find test names by looking at the class names in `python/tests/kat/t_*.py` files.

## How It Works

1. **Local Docker Registry**: A local registry container (`localhost:5000`) stores built images
2. **k3d Cluster**: A lightweight Kubernetes cluster runs in Docker
3. **Image Import**: Images are built locally and imported directly into k3d (no external push needed)
4. **Test Execution**: pytest runs the KAT tests against your local cluster

## Architecture

```
┌─────────────────────────────────────────┐
│  Your Mac (ARM64)                       │
│  ┌───────────────────────────────────┐  │
│  │ Docker Desktop                    │  │
│  │                                   │  │
│  │  ┌─────────────┐  ┌────────────┐ │  │
│  │  │ k3d Cluster │  │  Registry  │ │  │
│  │  │             │  │  :5000     │ │  │
│  │  │  - Pods     │←─┤            │ │  │
│  │  │  - Services │  │  - Images  │ │  │
│  │  └─────────────┘  └────────────┘ │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
         ↑
         │ kubectl & pytest
         │
    Your terminal
```

## Files

- **`README.md`** - This file
- **`get-envoy-image.sh`** - Downloads a compatible Envoy base image
- **`setup-environment.sh`** - One-time setup (k3d + registry)
- **`run-test.sh`** - Run a single KAT test
- **`setup-registry.sh`** - Sets up local Docker registry (called by setup-environment.sh)

## Environment Variables

These are set automatically by the scripts:

- `SKIP_BASE_PYTHON_PUSH=1` - Skip pushing base-python to remote registries
- `BUILD_ARCH=linux/arm64` - Build for ARM64 (adjust if on x86)
- `DEV_REGISTRY=localhost:5000` - Use local registry
- `DEV_KUBECONFIG=~/.kube/config` - Use k3d cluster
- `VERSION=v0.0.0-test` - Local development version tag

## Troubleshooting

### "k3d cluster not found"
Run `./setup-environment.sh` first.

### "Envoy image not found"
Run `./get-envoy-image.sh` to download a compatible version.

### Image pull errors in pods
The scripts automatically set `imagePullPolicy: IfNotPresent` and import images into k3d.
If you still see errors, manually import:
```bash
tools/bin/k3d image import localhost:5000/emissary:0.0.0-test
```

### Tests timeout
The k3d cluster might be slow. Wait a bit and try again. Check pod status:
```bash
tools/bin/kubectl get pods -A
```

## Cleanup

```bash
# Stop and remove k3d cluster
make ci/teardown-k3d

# Stop local registry
docker stop emissary-registry

# Remove local registry
docker rm emissary-registry
```

## Code Changes Required

The following files in the main codebase were modified to support local testing:

1. **`docker/base-python.docker.gen`** - Added `SKIP_BASE_PYTHON_PUSH` support
2. **`python/kat/harness.py`** - Fixed pytest 8.x compatibility
3. **`python/tests/integration/manifests/dummy_pod.yaml`** - Changed imagePullPolicy to IfNotPresent
4. **`python/tests/integration/manifests/kat_client_pod.yaml`** - Added imagePullPolicy: IfNotPresent

These changes are minimal and don't affect normal CI/CD workflows.

## Notes

- First build takes some time but subsequent runs are much faster
- Tests run against a real Kubernetes cluster, so they're closer to production than unit tests
- Each test can take 1-2 minutes to run as it sets up Kubernetes resources
