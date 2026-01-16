include $(dir $(lastword $(MAKEFILE_LIST)))tools.mk

# Compute lowercase name for image references
LCNAME := $(shell echo $(EMISSARY_NAME) | tr '[:upper:]' '[:lower:]')

# Set a dummy DEV_REGISTRY for CI to prevent errors in builder.mk
# This registry is never actually used - we only build local tags
# But builder.mk requires it to be set to avoid parse-time errors
# We also set CI_USE_LOCAL_IMAGES=true to signal to scripts that we're in local-only mode
ifeq ($(DEV_REGISTRY),)
  export DEV_REGISTRY := localhost:5000
  export CI_USE_LOCAL_IMAGES := true
endif

K3S_VERSION      ?= 1.22.17-k3s1
K3D_CLUSTER_NAME =
K3D_ARGS         = --k3s-arg=--disable=traefik@server:* --k3s-arg=--kubelet-arg=max-pods=255@server:* --k3s-arg=--egress-selector-mode=disabled@server:*
# This is modeled after
# https://github.com/nolar/setup-k3d-k3s/blob/v1.0.7/action.sh#L70-L77 and
# https://github.com/nolar/setup-k3d-k3s/blob/v1.0.7/action.yaml#L34-L46
ci/setup-k3d: $(tools/k3d) $(tools/kubectl)
	$(tools/k3d) cluster create --wait --image=docker.io/rancher/k3s:v$(subst +,-,$(K3S_VERSION)) $(K3D_ARGS) $(K3D_CLUSTER_NAME)
	while ! $(tools/kubectl) get serviceaccount default >/dev/null; do sleep 1; done
	$(tools/kubectl) version
.PHONY: ci/setup-k3d

ci/teardown-k3d: $(tools/k3d)
	$(tools/k3d) cluster delete || true
.PHONY: ci/teardown-k3d

# Build test images locally and import them into k3d cluster
# This avoids the need for a remote registry and secrets
ci/build-and-import-images: docker/$(LCNAME).docker.tag.local
ci/build-and-import-images: docker/test-auth.docker.tag.local
ci/build-and-import-images: docker/test-shadow.docker.tag.local
ci/build-and-import-images: docker/test-stats.docker.tag.local
ci/build-and-import-images: docker/kat-client.docker.tag.local
ci/build-and-import-images: docker/kat-server.docker.tag.local
ci/build-and-import-images: docker/base-envoy.docker.tag.local
ci/build-and-import-images: $(tools/k3d)
	@printf "$(CYN)==> $(GRN)Importing images into k3d cluster$(END)\n"
	$(tools/k3d) image import \
		$$(sed -n 2p docker/$(LCNAME).docker.tag.local) \
		$$(sed -n 2p docker/test-auth.docker.tag.local) \
		$$(sed -n 2p docker/test-shadow.docker.tag.local) \
		$$(sed -n 2p docker/test-stats.docker.tag.local) \
		$$(sed -n 2p docker/kat-client.docker.tag.local) \
		$$(sed -n 2p docker/kat-server.docker.tag.local)
.PHONY: ci/build-and-import-images

# Python integration test environment for CI (no registry required)
# This is a minimal version of python-integration-test-environment that doesn't
# require push-pytest-images or proxy (which both need DEV_REGISTRY)
ci/python-integration-test-environment: $(tools/kubestatus)
ci/python-integration-test-environment: $(tools/kubectl)
ci/python-integration-test-environment: python-virtual-environment
.PHONY: ci/python-integration-test-environment

# Build the test list file without requiring push-pytest-images
# This overrides the regular build-aux/.pytest-kat.txt.stamp target from builder.mk
# to remove the push-pytest-images dependency
build-aux/.pytest-kat.txt.stamp: $(OSS_HOME)/venv $(tools/kubectl) FORCE
	. venv/bin/activate && set -o pipefail && pytest --collect-only python/tests/kat 2>&1 | sed -En 's/.*<Function (.*)>/\1/p' | cut -d. -f1 | sort -u > $@

# CI-specific pytest targets that don't depend on python-integration-test-environment
# (which requires DEV_REGISTRY). Instead, they only depend on the minimal CI setup.
ci/pytest-kat-envoy3-tests-%: ci/python-integration-test-environment
ci/pytest-kat-envoy3-tests-%: ci/build-and-import-images
ci/pytest-kat-envoy3-tests-%: build-aux/pytest-kat.txt
	$(MAKE) pytest-run-tests PYTEST_ARGS="$$PYTEST_ARGS -k '$$($(tools/py-split-tests) $(subst -of-, ,$*) <build-aux/pytest-kat.txt)' python/tests/kat"
.PHONY: ci/pytest-kat-envoy3-tests-%
