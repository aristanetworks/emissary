import logging
import os
import sys

import pytest

from ambassador.utils import NullSecretHandler, parse_bool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s test %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("ambassador")

from ambassador import Config
from ambassador.fetch import ResourceFetcher
from ambassador.fetch.ambassador import AmbassadorProcessor
from ambassador.fetch.dependency import (
    DependencyManager,
    SecretDependency,
    ServiceDependency,
)
from ambassador.fetch.k8sobject import (
    KubernetesGVK,
    KubernetesObject,
    KubernetesObjectKey,
    KubernetesObjectScope,
)
from ambassador.fetch.k8sprocessor import (
    AggregateKubernetesProcessor,
    CountingKubernetesProcessor,
    DeduplicatingKubernetesProcessor,
    KubernetesProcessor,
)
from ambassador.fetch.location import LocationManager
from ambassador.fetch.resource import NormalizedResource, ResourceManager
from ambassador.utils import parse_yaml


def k8s_object_from_yaml(yaml: str) -> KubernetesObject:
    return KubernetesObject(parse_yaml(yaml)[0])



valid_mapping = k8s_object_from_yaml(
    """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: test
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: test.default
"""
)

valid_mapping_v1 = k8s_object_from_yaml(
    """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: test
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: test.default
"""
)

valid_tcpmapping = k8s_object_from_yaml(
    """
---
apiVersion: getambassador.io/v3alpha1
kind: TCPMapping
metadata:
  name: test-tcp
  namespace: default
spec:
  port: 8088
  service: test-tcp.default
"""
)


class TestKubernetesGVK:
    def test_legacy(self):
        gvk = KubernetesGVK("v1", "Service")

        assert gvk.api_version == "v1"
        assert gvk.kind == "Service"
        assert gvk.api_group is None
        assert gvk.version == "v1"
        assert gvk.domain == "service"

    def test_group(self):
        gvk = KubernetesGVK.for_ambassador("Mapping", version="v3alpha1")

        assert gvk.api_version == "getambassador.io/v3alpha1"
        assert gvk.kind == "Mapping"
        assert gvk.api_group == "getambassador.io"
        assert gvk.version == "v3alpha1"
        assert gvk.domain == "mapping.getambassador.io"


class TestKubernetesObject:
    def test_valid(self):
        assert valid_mapping.gvk.kind == "Mapping"
        assert valid_mapping.gvk.api_version == "getambassador.io/v3alpha1"
        assert valid_mapping.namespace == "default"
        assert valid_mapping.name == "test"
        assert valid_mapping.scope == KubernetesObjectScope.NAMESPACE
        assert valid_mapping.key == KubernetesObjectKey(
            valid_mapping.gvk, "default", "test"
        )
        assert valid_mapping.spec["prefix"] == "/test/"
        assert valid_mapping.spec["service"] == "test.default"

    def test_invalid(self):
        with pytest.raises(ValueError, match="not a valid Kubernetes object"):
            k8s_object_from_yaml("apiVersion: v1")


class TestNormalizedResource:
    def test_kubernetes_object_conversion(self):
        resource = NormalizedResource.from_kubernetes_object(valid_mapping)

        assert resource.rkey == f"{valid_mapping.name}.{valid_mapping.namespace}"
        assert resource.object["apiVersion"] == valid_mapping.gvk.api_version
        assert resource.object["kind"] == valid_mapping.kind
        assert resource.object["name"] == valid_mapping.name
        assert resource.object["namespace"] == valid_mapping.namespace
        assert resource.object["generation"] == valid_mapping.generation
        assert len(resource.object["metadata_labels"]) == 1
        assert resource.object["metadata_labels"]["ambassador_crd"] == resource.rkey
        assert resource.object["prefix"] == valid_mapping.spec["prefix"]
        assert resource.object["service"] == valid_mapping.spec["service"]


class TestLocationManager:
    def test_context_manager(self):
        lm = LocationManager()

        assert len(lm.previous) == 0

        assert lm.current.filename is None
        assert lm.current.ocount == 1

        with lm.push(filename="test", ocount=2) as loc:
            assert len(lm.previous) == 1
            assert lm.current == loc

            assert loc.filename == "test"
            assert loc.ocount == 2

            with lm.push_reset() as rloc:
                assert len(lm.previous) == 2
                assert lm.current == rloc

                assert rloc.filename == "test"
                assert rloc.ocount == 1

        assert len(lm.previous) == 0

        assert lm.current.filename is None
        assert lm.current.ocount == 1


class FinalizingKubernetesProcessor(KubernetesProcessor):
    finalized: bool = False

    def finalize(self):
        self.finalized = True


class TestAmbassadorProcessor:
    def test_mapping(self):
        aconf = Config()
        mgr = ResourceManager(logger, aconf, DependencyManager([]))

        assert AmbassadorProcessor(mgr).try_process(valid_mapping)
        assert len(mgr.elements) == 1

        aconf.load_all(mgr.elements)
        assert len(aconf.errors) == 0

        mappings = aconf.get_config("mappings")
        assert mappings
        assert len(mappings) == 1

        mapping = next(iter(mappings.values()))
        assert mapping.apiVersion == valid_mapping.gvk.api_version
        assert mapping.name == valid_mapping.name
        assert mapping.namespace == valid_mapping.namespace
        assert mapping.prefix == valid_mapping.spec["prefix"]
        assert mapping.service == valid_mapping.spec["service"]

    def test_mapping_v1(self):
        aconf = Config()
        mgr = ResourceManager(logger, aconf, DependencyManager([]))

        assert AmbassadorProcessor(mgr).try_process(valid_mapping_v1)
        assert len(mgr.elements) == 1
        print(f"mgr.elements[0]={mgr.elements[0].apiVersion}")

        aconf.load_all(mgr.elements)
        assert len(aconf.errors) == 0

        mappings = aconf.get_config("mappings")
        assert mappings
        assert len(mappings) == 1

        mapping = next(iter(mappings.values()))
        assert mapping.apiVersion == valid_mapping_v1.gvk.api_version
        assert mapping.name == valid_mapping_v1.name
        assert mapping.namespace == valid_mapping_v1.namespace
        assert mapping.prefix == valid_mapping_v1.spec["prefix"]
        assert mapping.service == valid_mapping_v1.spec["service"]


class TestAggregateKubernetesProcessor:
    def test_aggregation(self):
        aconf = Config()

        fp = FinalizingKubernetesProcessor()

        p = AggregateKubernetesProcessor(
            [
                CountingKubernetesProcessor(aconf, valid_tcpmapping.gvk, "test_1"),
                CountingKubernetesProcessor(aconf, valid_mapping.gvk, "test_2"),
                fp,
            ]
        )

        assert len(p.kinds()) == 2

        assert p.try_process(valid_mapping)
        assert p.try_process(valid_mapping)

        assert aconf.get_count("test_1") == 0
        assert aconf.get_count("test_2") == 2

        p.finalize()
        assert fp.finalized, "Aggregate processor did not call finalizers"


class TestDeduplicatingKubernetesProcessor:
    def test_deduplication(self):
        aconf = Config()

        p = DeduplicatingKubernetesProcessor(
            CountingKubernetesProcessor(aconf, valid_mapping.gvk, "test")
        )

        assert p.try_process(valid_mapping)
        assert p.try_process(valid_mapping)
        assert p.try_process(valid_mapping)

        assert aconf.get_count("test") == 1


class TestCountingKubernetesProcessor:
    def test_count(self):
        aconf = Config()

        p = CountingKubernetesProcessor(aconf, valid_mapping.gvk, "test")

        assert p.try_process(valid_mapping), "Processor rejected matching resource"
        assert p.try_process(valid_mapping), "Processor rejected matching resource (again)"

        assert aconf.get_count("test") == 2, "Processor did not increment counter"


class TestDependencyManager:
    def setup_method(self):
        self.deps = DependencyManager(
            [
                SecretDependency(),
                ServiceDependency(),
            ]
        )

    def test_cyclic(self):
        a = self.deps.for_instance(object())
        b = self.deps.for_instance(object())

        a.provide(SecretDependency)
        a.want(ServiceDependency)
        b.provide(ServiceDependency)
        b.want(SecretDependency)

        with pytest.raises(ValueError):
            self.deps.sorted_watt_keys()

    def test_sort(self):
        a = self.deps.for_instance(object())
        b = self.deps.for_instance(object())

        a.want(SecretDependency)
        a.want(ServiceDependency)
        b.provide(SecretDependency)
        a.provide(ServiceDependency)

        assert self.deps.sorted_watt_keys() == ["secret", "service"]


if __name__ == "__main__":
    pytest.main(sys.argv)
