import json
from typing import Generator, Tuple, Union

from abstract_tests import HTTP, AmbassadorTest, Node, ServiceType
from kat.harness import Query


class MaxConcurrentStreamsTest(AmbassadorTest):
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
