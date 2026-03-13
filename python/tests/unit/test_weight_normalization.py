import logging
import json
import pytest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s test %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("ambassador")

from ambassador import IR, Config
from ambassador.fetch import ResourceFetcher
from ambassador.utils import NullSecretHandler


def _get_ir_config(yaml):
    aconf = Config()
    fetcher = ResourceFetcher(logger, aconf)
    fetcher.parse_yaml(yaml, k8s=True)
    aconf.load_all(fetcher.sorted())

    secret_handler = NullSecretHandler(logger, None, None, "0")
    ir = IR(aconf, file_checker=lambda path: True, secret_handler=secret_handler)

    assert ir
    return ir


@pytest.mark.compilertest
def test_weight_normalization_over_100():
    """Test that weights exceeding 100 are normalized proportionally"""
    yaml = """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-blue
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: blue.default
  weight: 60
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-green
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: green.default
  weight: 80
"""

    ir = _get_ir_config(yaml)
    
    # Should not have errors
    errors = ir.aconf.errors
    assert len(errors) == 0, f"Expected no errors but got {json.dumps(errors, sort_keys=True, indent=4)}"
    
    # Find the mapping group
    found_group = None
    for group in ir.groups.values():
        if group.prefix == "/test/":
            found_group = group
            break
    
    assert found_group is not None, "Expected to find /test/ mapping group"
    assert len(found_group.mappings) == 2, f"Expected 2 mappings but found {len(found_group.mappings)}"
    
    # Check that weights are normalized
    # Original weights: 60 + 80 = 140
    # Normalized: 60/140 * 100 = 42.86 (rounds to 43), 80/140 * 100 = 57.14
    # Cumulative: 43, 100 (last one is forced to 100)
    weights = [m._weight for m in found_group.mappings]
    
    # The first mapping should have cumulative weight around 43
    # The second mapping should have cumulative weight of 100
    assert weights[0] in [42, 43], f"Expected first weight to be ~43, got {weights[0]}"
    assert weights[1] == 100, f"Expected second weight to be 100, got {weights[1]}"


@pytest.mark.compilertest
def test_weight_normalization_equal_100():
    """Test that weights equaling 100 work correctly (no normalization needed)"""
    yaml = """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-blue
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: blue.default
  weight: 30
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-green
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: green.default
  weight: 70
"""

    ir = _get_ir_config(yaml)
    
    # Should not have errors
    errors = ir.aconf.errors
    assert len(errors) == 0, f"Expected no errors but got {json.dumps(errors, sort_keys=True, indent=4)}"
    
    # Find the mapping group
    found_group = None
    for group in ir.groups.values():
        if group.prefix == "/test/":
            found_group = group
            break
    
    assert found_group is not None, "Expected to find /test/ mapping group"
    assert len(found_group.mappings) == 2, f"Expected 2 mappings but found {len(found_group.mappings)}"
    
    # Check that weights are cumulative as expected (no normalization)
    weights = [m._weight for m in found_group.mappings]
    assert weights[0] == 30, f"Expected first weight to be 30, got {weights[0]}"
    assert weights[1] == 100, f"Expected second weight to be 100, got {weights[1]}"


@pytest.mark.compilertest
def test_weight_normalization_three_mappings():
    """Test normalization with three mappings exceeding 100"""
    yaml = """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-blue
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: blue.default
  weight: 50
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-green
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: green.default
  weight: 50
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-red
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: red.default
  weight: 50
"""

    ir = _get_ir_config(yaml)

    # Should not have errors
    errors = ir.aconf.errors
    assert len(errors) == 0, f"Expected no errors but got {json.dumps(errors, sort_keys=True, indent=4)}"

    # Find the mapping group
    found_group = None
    for group in ir.groups.values():
        if group.prefix == "/test/":
            found_group = group
            break

    assert found_group is not None, "Expected to find /test/ mapping group"
    assert len(found_group.mappings) == 3, f"Expected 3 mappings but found {len(found_group.mappings)}"

    # Check that weights are normalized
    # Original weights: 50 + 50 + 50 = 150
    # Normalized: each 50/150 * 100 = 33.33
    # Cumulative: 33, 67, 100 (last one is forced to 100)
    weights = [m._weight for m in found_group.mappings]

    # First two should be around 33 and 67
    assert weights[0] in [33, 34], f"Expected first weight to be ~33, got {weights[0]}"
    assert weights[1] in [66, 67], f"Expected second weight to be ~67, got {weights[1]}"
    assert weights[2] == 100, f"Expected third weight to be 100, got {weights[2]}"


@pytest.mark.compilertest
def test_weight_normalization_less_than_100():
    """Test that weights less than 100 work correctly (no normalization needed)"""
    yaml = """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-blue
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: blue.default
  weight: 20
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-green
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: green.default
  weight: 30
"""

    ir = _get_ir_config(yaml)

    # Should not have errors
    errors = ir.aconf.errors
    assert len(errors) == 0, f"Expected no errors but got {json.dumps(errors, sort_keys=True, indent=4)}"

    # Find the mapping group
    found_group = None
    for group in ir.groups.values():
        if group.prefix == "/test/":
            found_group = group
            break

    assert found_group is not None, "Expected to find /test/ mapping group"
    assert len(found_group.mappings) == 2, f"Expected 2 mappings but found {len(found_group.mappings)}"

    # Check that weights are cumulative as expected (no normalization)
    weights = [m._weight for m in found_group.mappings]
    assert weights[0] == 20, f"Expected first weight to be 20, got {weights[0]}"
    assert weights[1] == 50, f"Expected second weight to be 50, got {weights[1]}"


@pytest.mark.compilertest
def test_single_mapping_with_explicit_weight():
    """Test that a single mapping with explicit weight < 100 still gets 100% traffic"""
    yaml = """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-blue
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: blue.default
  weight: 50
"""

    ir = _get_ir_config(yaml)

    # Should not have errors
    errors = ir.aconf.errors
    assert len(errors) == 0, f"Expected no errors but got {json.dumps(errors, sort_keys=True, indent=4)}"

    # Find the mapping group
    found_group = None
    for group in ir.groups.values():
        if group.prefix == "/test/":
            found_group = group
            break

    assert found_group is not None, "Expected to find /test/ mapping group"
    assert len(found_group.mappings) == 1, f"Expected 1 mapping but found {len(found_group.mappings)}"

    # Single mapping should always get 100% regardless of explicit weight
    assert found_group.mappings[0]._weight == 100, f"Expected weight to be 100, got {found_group.mappings[0]._weight}"


@pytest.mark.compilertest
def test_weightless_mappings_only():
    """Test that mappings without weight attribute share traffic equally"""
    yaml = """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-blue
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: blue.default
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-green
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: green.default
"""

    ir = _get_ir_config(yaml)

    # Should not have errors
    errors = ir.aconf.errors
    assert len(errors) == 0, f"Expected no errors but got {json.dumps(errors, sort_keys=True, indent=4)}"

    # Find the mapping group
    found_group = None
    for group in ir.groups.values():
        if group.prefix == "/test/":
            found_group = group
            break

    assert found_group is not None, "Expected to find /test/ mapping group"
    assert len(found_group.mappings) == 2, f"Expected 2 mappings but found {len(found_group.mappings)}"

    # Weightless mappings should share equally: 50% each
    weights = [m._weight for m in found_group.mappings]
    assert weights[0] == 50, f"Expected first weight to be 50, got {weights[0]}"
    assert weights[1] == 100, f"Expected second weight to be 100, got {weights[1]}"


@pytest.mark.compilertest
def test_mixed_weighted_and_weightless_over_100():
    """Test mixed weighted and weightless mappings when weighted total exceeds 100"""
    yaml = """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-blue
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: blue.default
  weight: 80
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-green
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: green.default
  weight: 60
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-red
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: red.default
"""

    ir = _get_ir_config(yaml)

    # Should not have errors
    errors = ir.aconf.errors
    assert len(errors) == 0, f"Expected no errors but got {json.dumps(errors, sort_keys=True, indent=4)}"

    # Find the mapping group
    found_group = None
    for group in ir.groups.values():
        if group.prefix == "/test/":
            found_group = group
            break

    assert found_group is not None, "Expected to find /test/ mapping group"
    assert len(found_group.mappings) == 3, f"Expected 3 mappings but found {len(found_group.mappings)}"

    # Weighted mappings (80 + 60 = 140) should be normalized to 100
    # 80/140 * 100 = 57.14 (rounds to 57)
    # 60/140 * 100 = 42.86 (last one forced to 100)
    # Weightless mapping gets 0 since weighted already at 100
    weights = [m._weight for m in found_group.mappings]

    # First two are the weighted mappings (normalized)
    assert weights[0] in [57, 58], f"Expected first weight to be ~57, got {weights[0]}"
    assert weights[1] == 100, f"Expected second weight to be 100, got {weights[1]}"
    # Third is weightless, should get 0 since weighted mappings already at 100
    assert weights[2] == 100, f"Expected third weight to be 100, got {weights[2]}"


@pytest.mark.compilertest
def test_mixed_weighted_and_weightless_under_100():
    """Test mixed weighted and weightless mappings when weighted total is under 100"""
    yaml = """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-blue
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: blue.default
  weight: 30
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-green
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: green.default
  weight: 20
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-red
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: red.default
"""

    ir = _get_ir_config(yaml)

    # Should not have errors
    errors = ir.aconf.errors
    assert len(errors) == 0, f"Expected no errors but got {json.dumps(errors, sort_keys=True, indent=4)}"

    # Find the mapping group
    found_group = None
    for group in ir.groups.values():
        if group.prefix == "/test/":
            found_group = group
            break

    assert found_group is not None, "Expected to find /test/ mapping group"
    assert len(found_group.mappings) == 3, f"Expected 3 mappings but found {len(found_group.mappings)}"

    # Weighted: 30 + 20 = 50, leaving 50 for weightless
    # Weightless gets remaining 50
    weights = [m._weight for m in found_group.mappings]

    assert weights[0] == 30, f"Expected first weight to be 30, got {weights[0]}"
    assert weights[1] == 50, f"Expected second weight to be 50, got {weights[1]}"
    assert weights[2] == 100, f"Expected third weight to be 100, got {weights[2]}"


@pytest.mark.compilertest
def test_weight_zero():
    """Test that a mapping with weight 0 is handled correctly"""
    yaml = """
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-blue
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: blue.default
  weight: 0
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: mapping-green
  namespace: default
spec:
  hostname: "*"
  prefix: /test/
  service: green.default
  weight: 100
"""

    ir = _get_ir_config(yaml)

    # Should not have errors
    errors = ir.aconf.errors
    assert len(errors) == 0, f"Expected no errors but got {json.dumps(errors, sort_keys=True, indent=4)}"

    # Find the mapping group
    found_group = None
    for group in ir.groups.values():
        if group.prefix == "/test/":
            found_group = group
            break

    assert found_group is not None, "Expected to find /test/ mapping group"
    assert len(found_group.mappings) == 2, f"Expected 2 mappings but found {len(found_group.mappings)}"

    # Weight 0 + 100 = 100, no normalization
    weights = [m._weight for m in found_group.mappings]
    assert weights[0] == 0, f"Expected first weight to be 0, got {weights[0]}"
    assert weights[1] == 100, f"Expected second weight to be 100, got {weights[1]}"

