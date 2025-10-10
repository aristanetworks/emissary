import json
from typing import Generator, Tuple, Union

from abstract_tests import HTTP, AmbassadorTest, Node, ServiceType
from kat.harness import Query


class MappingMaxConcurrentStreamsTest(AmbassadorTest):
    target: ServiceType

    def init(self):
        self.target = HTTP()

    def config(self) -> Generator[Union[str, Tuple[Node, str]], None, None]:
        yield self, self.format(
            """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
name: mapping-max-concurrent-streams
hostname: "*"
prefix: /test-mapping-streams/
service: {self.target.path.fqdn}
grpc: true
max_concurrent_streams: 42
"""
        )
        yield self, self.format(
            """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
name: config__dump
hostname: "*"
prefix: /config_dump
rewrite: /config_dump
service: http://127.0.0.1:8001
"""
        )

    def queries(self):
        yield Query(self.url("config_dump"), phase=2)

    def check(self):
        expected_val = "42"  # Envoy config stores this as a string
        found_max_concurrent_streams = False
        
        assert self.results[0].body
        body = json.loads(self.results[0].body)
        
        for config_obj in body.get("configs"):
            if config_obj.get("@type") == "type.googleapis.com/envoy.admin.v3.ClustersConfigDump":
                clusters = config_obj.get("dynamic_active_clusters", [])
                
                for cluster_obj in clusters:
                    cluster = cluster_obj.get("cluster", {})
                    cluster_name = cluster.get("name", "")
                    
                    # Look for our target cluster
                    if "test-mapping-streams" in cluster_name or self.target.path.fqdn.replace(":", "_") in cluster_name:
                        http2_options = cluster.get("http2_protocol_options", {})
                        actual_val = http2_options.get("max_concurrent_streams")

                        if actual_val == expected_val:
                            found_max_concurrent_streams = True
                            break
                        elif actual_val is not None:
                            assert False, f"Expected max_concurrent_streams = {expected_val}, Got {actual_val} in cluster {cluster_name}"
                
                if found_max_concurrent_streams:
                    break
        
        assert found_max_concurrent_streams, f"Expected to find max_concurrent_streams = {expected_val} in cluster http2_protocol_options, but it was not found"
