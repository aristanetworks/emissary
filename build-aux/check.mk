include build-aux/tools.mk

#
# Auxiliary Docker images needed for the tests

# Keep this list in-sync with python/tests/integration/manifests.py
push-pytest-images: docker/$(LCNAME).docker.push.remote
push-pytest-images: docker/test-auth.docker.push.remote
push-pytest-images: docker/test-shadow.docker.push.remote
push-pytest-images: docker/test-stats.docker.push.remote
push-pytest-images: docker/kat-client.docker.push.remote
push-pytest-images: docker/kat-server.docker.push.remote
.PHONY: push-pytest-images

# test-{auth,shadow,stats}.docker
test_svcs = auth shadow stats
$(foreach svc,$(test_svcs),docker/test-$(svc).docker): docker/%.docker: docker/%/Dockerfile FORCE
	docker build --iidfile=$@ $(<D)
clean: $(foreach svc,$(test_svcs),docker/test-$(svc).docker.clean)

# kat-client.docker
docker/kat-client.docker: docker/kat-client/Dockerfile vendor api pkg cmd/kat-client FORCE
	docker build --platform="$(BUILD_ARCH)" \
	  -f docker/kat-client/Dockerfile \
	  -t $(LCNAME).local/kat-client:latest \
	  --iidfile=$@ \
	  .
clean: docker/kat-client.docker.clean

# kat-server.docker
docker/kat-server/server.crt: $(tools/testcert-gen)
	mkdir -p $(@D)
	$(tools/testcert-gen) --out-cert=$@ --out-key=/dev/null --hosts=kat-server.test.getambassador.io
docker/kat-server/server.key: $(tools/testcert-gen)
	mkdir -p $(@D)
	$(tools/testcert-gen) --out-cert=/dev/null --out-key=$@ --hosts=kat-server.test.getambassador.io
docker/kat-server.docker: docker/kat-server/Dockerfile docker/kat-server/server.crt docker/kat-server/server.key vendor api pkg cmd/kat-server FORCE
	docker build --platform="$(BUILD_ARCH)" \
	  -f docker/kat-server/Dockerfile \
	  -t $(LCNAME).local/kat-server:latest \
	  --iidfile=$@ \
	  .
clean: docker/kat-server.docker.clean

#
# Helm tests

test-chart-values.yaml: docker/$(LCNAME).docker.push.remote build-aux/check.mk
	{ \
	  echo 'test:'; \
	  echo '  enabled: true'; \
	  echo 'image:'; \
	  sed -E -n '2s/^(.*):.*/  repository: \1/p' < $<; \
	  sed -E -n '2s/.*:/  tag: /p' < $<; \
	} >$@
clean: test-chart-values.yaml.rm
build-output/chart-%/ci: build-output/chart-% test-chart-values.yaml
	rm -rf $@
	cp -a $@.in $@
	for file in $@/*-values.yaml; do cat test-chart-values.yaml >> "$$file"; done

test-chart: $(tools/ct) $(tools/kubectl) $(chart_dir)/ci build-output/yaml-$(patsubst v%,%,$(VERSION)) $(if $(DEV_USE_IMAGEPULLSECRET),push-pytest-images $(OSS_HOME)/venv)
ifneq ($(DEV_USE_IMAGEPULLSECRET),)
	. venv/bin/activate && KUBECONFIG=$(DEV_KUBECONFIG) python3 -c 'from tests.integration.utils import install_crds; install_crds()'
else
	$(tools/kubectl) --kubeconfig=$(DEV_KUBECONFIG) apply -f build-output/yaml-$(patsubst v%,%,$(VERSION))/emissary-crds.yaml
endif
	$(tools/kubectl) --kubeconfig=$(DEV_KUBECONFIG) --namespace=emissary-system wait --timeout=90s --for=condition=available Deployments/emissary-apiext
	cd $(chart_dir) && KUBECONFIG=$(DEV_KUBECONFIG) $(abspath $(tools/ct)) install --config=./ct.yaml
.PHONY: test-chart

#
# Other

clean: .pytest_cache.rm-r .coverage.rm

dtest.clean:
	docker container list --filter=label=scope=dtest --quiet | xargs -r docker container kill
clean: dtest.clean
