import json
from typing import Generator, Tuple, Union

from abstract_tests import HTTP, AmbassadorTest, Node, ServiceType
from kat.harness import Query


class DownstreamMaxConcurrentStreamsTest(AmbassadorTest):
    target: ServiceType

    def init(self):
        self.target = HTTP()

    def config(self) -> Generator[Union[str, Tuple[Node, str]], None, None]:
        yield self, self.format(
            """
---
apiVersion: getambassador.io/v3alpha1
kind: Module
name: ambassador
ambassador_id: [{self.ambassador_id}]
config:
  downstream_max_concurrent_streams: 100
"""
        )
        yield self, self.format(
            """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
name:  config__dump
hostname: "*"
prefix: /config_dump
rewrite: /config_dump
service: http://127.0.0.1:8001
"""
        )

    def queries(self):
        yield Query(self.url("config_dump"), phase=2)

    def check(self):
        expected_val = 100
        actual_val = -1
        assert self.results[0].body
        body = json.loads(self.results[0].body)
        for config_obj in body.get("configs"):
            if config_obj.get("@type") == "type.googleapis.com/envoy.admin.v3.ListenersConfigDump":
                listeners = config_obj.get("dynamic_listeners")
                found_max_concurrent_streams = False
                for listener_obj in listeners:
                    listener = listener_obj.get("active_state").get("listener")
                    filter_chains = listener.get("filter_chains")
                    for filters in filter_chains:
                        for filter in filters.get("filters"):
                            if (
                                filter.get("name")
                                == "envoy.filters.network.http_connection_manager"
                            ):
                                filter_config = filter.get("typed_config")
                                http2_protocol_options = filter_config.get(
                                    "http2_protocol_options"
                                )
                                if http2_protocol_options:
                                    actual_val = http2_protocol_options.get(
                                        "max_concurrent_streams", ""
                                    )
                                    if actual_val != "":
                                        if actual_val == expected_val:
                                            found_max_concurrent_streams = True
                                    else:
                                        assert (
                                            False
                                        ), "Expected to find http2_protocol_options.max_concurrent_streams property on listener"
                                else:
                                    assert (
                                        False
                                    ), "Expected to find http2_protocol_options property on listener"
                assert (
                    found_max_concurrent_streams
                ), "Expected http2_protocol_options.max_concurrent_streams = {}, Got http2_protocol_options.max_concurrent_streams = {}".format(
                    expected_val, actual_val
                )

class UpstreamMaxConcurrentStreamsTest(AmbassadorTest):
    target: ServiceType

    def init(self):
        self.target = HTTP()

    def config(self) -> Generator[Union[str, Tuple[Node, str]], None, None]:
        yield self, self.format(
            """
---
apiVersion: getambassador.io/v3alpha1
kind: Module
name: ambassador
ambassador_id: [{self.ambassador_id}]
config:
  upstream_max_concurrent_streams: 150
"""
        )
        yield self, self.format(
            """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
name: grpc_mapping
ambassador_id: [{self.ambassador_id}]
hostname: "*"
prefix: /grpc/
service: http://{self.target.path.fqdn}
grpc: true
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
        expected_val = 150

        # Parse the config dump response
        assert self.results[0].body, "No response body received"
        body = json.loads(self.results[0].body)

        # Find the clusters configuration
        clusters_config = self._find_clusters_config(body)
        assert clusters_config, "ClustersConfigDump not found in response"

        # Look for our gRPC cluster and validate max_concurrent_streams
        actual_val = self._find_grpc_max_concurrent_streams(clusters_config)
        assert actual_val == expected_val, (
            f"Expected upstream max_concurrent_streams = {expected_val}, "
            f"but got {actual_val}"
        )

    def _find_clusters_config(self, body):
        """Find the ClustersConfigDump section in the config response"""
        for config_obj in body.get("configs", []):
            if config_obj.get("@type") == "type.googleapis.com/envoy.admin.v3.ClustersConfigDump":
                return config_obj
        return None

    def _find_grpc_max_concurrent_streams(self, clusters_config):
        """Find max_concurrent_streams value from our gRPC cluster"""
        clusters = clusters_config.get("dynamic_active_clusters", [])

        # Print available cluster names later for debugging purposes if failed
        cluster_names = []
        for cluster_obj in clusters:
            cluster = cluster_obj.get("cluster", {})
            cluster_name = cluster.get("name", "")
            cluster_names.append(cluster_name)

        for cluster_obj in clusters:
            cluster = cluster_obj.get("cluster", {})
            http2_options = cluster.get("http2_protocol_options")

            if http2_options:
                max_streams = http2_options.get("max_concurrent_streams")
                if max_streams:
                    return max_streams

        assert False, f"No gRPC cluster found with max_concurrent_streams. Available clusters: {cluster_names}"
