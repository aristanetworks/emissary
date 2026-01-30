# Go-control-plane generation targets
#
# This file contains the logic for vendoring and patching go-control-plane
# to work with our Envoy protobuf definitions.

include $(OSS_HOME)/build-aux/prelude.mk

# How to set ENVOY_GO_CONTROL_PLANE_COMMIT: In github.com/envoyproxy/go-control-plane.git, the majority
# of commits have a commit message of the form "Mirrored from envoyproxy/envoy @ ${envoy.git_commit}".
# Look for the most recent one that names a commit that is an ancestor of the Envoy version we're using.
# If there are commits not of that form immediately following that commit, you can take them in too (but
# that's pretty uncommon).
ENVOY_GO_CONTROL_PLANE_COMMIT = f888b4f71207d0d268dee7cb824de92848da9ede

# The unmodified go-control-plane
$(OSS_HOME)/_cxx/go-control-plane: FORCE
	@echo "Getting Envoy go-control-plane sources..."
# Ensure that GIT_DIR and GIT_WORK_TREE are unset so that `git bisect`
# and friends work properly.
	@PS4=; set -ex; { \
	    unset GIT_DIR GIT_WORK_TREE; \
	    git init $@; \
	    cd $@; \
	    if git remote get-url origin &>/dev/null; then \
	        git remote set-url origin https://github.com/envoyproxy/go-control-plane; \
	    else \
	        git remote add origin https://github.com/envoyproxy/go-control-plane; \
	    fi; \
	    git fetch --tags origin; \
	    git checkout $(ENVOY_GO_CONTROL_PLANE_COMMIT); \
	}

# The go-control-plane patched for our version of the protobufs
$(OSS_HOME)/pkg/envoy-control-plane: $(OSS_HOME)/_cxx/go-control-plane FORCE
	rm -rf $@
	@PS4=; set -ex; { \
	  unset GIT_DIR GIT_WORK_TREE; \
	  tmpdir=$$(mktemp -d); \
	  trap 'rm -rf "$$tmpdir"' EXIT; \
	  cd "$$tmpdir"; \
	  cd $(OSS_HOME)/_cxx/go-control-plane; \
	  cp -r $$(git ls-files ':[A-Z]*' ':!Dockerfile*' ':!Makefile') pkg/* ratelimit "$$tmpdir"; \
	  find "$$tmpdir" -name '*.go' -exec sed -E -i.bak \
	    -e 's,github\.com/envoyproxy/go-control-plane/pkg,github.com/emissary-ingress/emissary/v3/pkg/envoy-control-plane,g' \
	    -e 's,github\.com/envoyproxy/go-control-plane/envoy,github.com/emissary-ingress/emissary/v3/pkg/api/envoy,g' \
		-e 's,github\.com/envoyproxy/go-control-plane/ratelimit,github.com/emissary-ingress/emissary/v3/pkg/envoy-control-plane/ratelimit,g' \
	    -- {} +; \
	  sed -i.bak -e 's/^package/\n&/' "$$tmpdir/log/log_test.go"; \
	  find "$$tmpdir" -name '*.bak' -delete; \
	  mv "$$tmpdir" $(abspath $@); \
	}
	cd $(OSS_HOME) && gofmt -w -s ./pkg/envoy-control-plane/

$(OSS_HOME)/_cxx/go-control-plane.clean: %.clean:
	rm -rf $*
clobber: $(OSS_HOME)/_cxx/go-control-plane.clean
