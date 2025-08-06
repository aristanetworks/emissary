import logging

import pytest

from tests.utils import module_and_mapping_manifests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s test %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("ambassador")

from ambassador import IR, Config, EnvoyConfig
from ambassador.fetch import ResourceFetcher
from ambassador.utils import NullSecretHandler
from tests.utils import default_listener_manifests


def _get_envoy_config(yaml):
    aconf = Config()
    fetcher = ResourceFetcher(logger, aconf)
    fetcher.parse_yaml(default_listener_manifests() + yaml, k8s=True)

    aconf.load_all(fetcher.sorted())

    secret_handler = NullSecretHandler(logger, None, None, "0")

    ir = IR(aconf, file_checker=lambda path: True, secret_handler=secret_handler)

    assert ir

    return EnvoyConfig.generate(ir)

def _check_windows_value(conf, expected_connection_value, expected_stream_value):
    if conf is None:
        return False
    http2_protocol_options = conf.get("http2_protocol_options", None)
    assert (
        http2_protocol_options is not None
    ), f"http2_protocol_options not found in: {conf}"
    initial_stream_window_size = http2_protocol_options.get("initial_stream_window_size", None)
    assert expected_stream_value == int (
        initial_stream_window_size
    ), "initial_stream_window_size is not the expected value {}".format(initial_stream_window_size, expected_stream_value)
    initial_connection_window_size = http2_protocol_options.get("initial_connection_window_size", None)
    assert expected_connection_value == int (
        initial_connection_window_size
    ), "initial_connection_window_size {} is not the expected value {}".format(initial_connection_window_size, expected_connection_value)
    return True 

@pytest.mark.compilertest
def test_initial_windows_size_v3():
    yaml = """
---
apiVersion: getambassador.io/v3alpha1
kind: Module
metadata:
  name: ambassador
  namespace: default
spec:
  config:
    upstream_initial_stream_window_size: 12345
    upstream_initial_connection_window_size: 23456
    downstream_initial_stream_window_size: 34567
    downstream_initial_connection_window_size: 45678
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: ambassador
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: test:9999
  grpc: true
"""
    econf = _get_envoy_config(yaml)

    expected_upstream_stream_window_size = 12345
    expected_upstream_connection_window_size = 23456
    
    expected_downstream_stream_window_size = 34567
    expected_downstream_connection_window_size = 45678

    keys_found = False

    conf = econf.as_dict()
    for listener in conf["static_resources"]["listeners"]:
        for filter_chain in listener["filter_chains"]:
            for f in filter_chain["filters"]:
                keys_found = keys_found or _check_windows_value(f["typed_config"],
                                     expected_downstream_connection_window_size,
                                     expected_downstream_stream_window_size)
    assert keys_found, "initial_stream_window_size and initial_connection_window_size must be found listeners"
    keys_found = False
    for cluster in conf["static_resources"]["clusters"]:
        http2_protocol_options = cluster.get("http2_protocol_options", None)
        # not all clusters are http2/grpc clusters
        if http2_protocol_options is not None:
            keys_found = keys_found or _check_windows_value(cluster,
                                                            expected_upstream_connection_window_size,
                                                            expected_upstream_stream_window_size)
    assert keys_found, "initial_stream_window_size and initial_connection_window_size must be found in 1 cluster"
