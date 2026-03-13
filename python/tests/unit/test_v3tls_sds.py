"""
Unit tests for V3TLSContext SDS (Secret Discovery Service) methods.

These tests exercise add_context(), update_tls_certificate_sds(), and
update_validation_context_sds() directly using a lightweight mock IRTLSContext,
without needing a full IR or Envoy config compilation.
"""
import pytest

from ambassador.envoy.v3.v3tls import V3TLSContext


class MockIRTLSContext(dict):
    """Minimal stand-in for IRTLSContext for use in V3TLSContext.add_context() tests."""

    def __init__(self, secret_info=None, use_sds=False, is_fallback=False):
        super().__init__()
        self.use_sds = use_sds
        self.is_fallback = is_fallback
        self["secret_info"] = secret_info or {}


SDS_CLUSTER = "sds_cluster"


def _sds_config_for(name: str) -> dict:
    """Return the expected SDS config structure for a given secret name."""
    return {
        "name": name,
        "sds_config": {
            "api_config_source": {
                "api_type": "GRPC",
                "transport_api_version": "V3",
                "grpc_services": [{"envoy_grpc": {"cluster_name": SDS_CLUSTER}}],
            },
            "resource_api_version": "V3",
        },
    }


# ---------------------------------------------------------------------------
# update_tls_certificate_sds
# ---------------------------------------------------------------------------


@pytest.mark.compilertest
def test_update_tls_certificate_sds_structure():
    """Generated SDS cert config has the correct Envoy structure."""
    ctx = V3TLSContext()
    ctx.update_tls_certificate_sds("default/my-secret")

    configs = ctx.get_common().get("tls_certificate_sds_secret_configs", [])
    assert len(configs) == 1
    assert configs[0] == _sds_config_for("default/my-secret")


@pytest.mark.compilertest
def test_update_tls_certificate_sds_no_duplicates():
    """Calling update_tls_certificate_sds twice with the same name adds only one entry."""
    ctx = V3TLSContext()
    ctx.update_tls_certificate_sds("default/my-secret")
    ctx.update_tls_certificate_sds("default/my-secret")

    configs = ctx.get_common().get("tls_certificate_sds_secret_configs", [])
    assert len(configs) == 1


@pytest.mark.compilertest
def test_update_tls_certificate_sds_multiple_different():
    """Different names each get their own entry."""
    ctx = V3TLSContext()
    ctx.update_tls_certificate_sds("ns-a/secret-a")
    ctx.update_tls_certificate_sds("ns-b/secret-b")

    configs = ctx.get_common().get("tls_certificate_sds_secret_configs", [])
    assert len(configs) == 2
    assert configs[0]["name"] == "ns-a/secret-a"
    assert configs[1]["name"] == "ns-b/secret-b"


# ---------------------------------------------------------------------------
# update_validation_context_sds
# ---------------------------------------------------------------------------


@pytest.mark.compilertest
def test_update_validation_context_sds_structure():
    """Generated SDS validation config has the correct Envoy structure."""
    ctx = V3TLSContext()
    ctx.update_validation_context_sds("default/ca-secret")

    sds_config = ctx.get_common().get("validation_context_sds_secret_config")
    assert sds_config == _sds_config_for("default/ca-secret")


@pytest.mark.compilertest
def test_update_validation_context_sds_overwrites():
    """Last call wins — only one validation_context_sds_secret_config exists."""
    ctx = V3TLSContext()
    ctx.update_validation_context_sds("default/ca-first")
    ctx.update_validation_context_sds("default/ca-second")

    sds_config = ctx.get_common()["validation_context_sds_secret_config"]
    assert sds_config["name"] == "default/ca-second"


# ---------------------------------------------------------------------------
# add_context — SDS mode
# ---------------------------------------------------------------------------


@pytest.mark.compilertest
def test_add_context_sds_server_cert():
    """SDS mode: server cert is served via tls_certificate_sds_secret_configs, not tls_certificates."""
    ir_ctx = MockIRTLSContext(
        use_sds=True,
        secret_info={
            "sds_cert_name": "default/my-secret",
            "cert_chain_file": "/path/to/cert",
            "private_key_file": "/path/to/key",
        },
    )

    ctx = V3TLSContext()
    ctx.add_context(ir_ctx)

    common = ctx.get_common()
    assert "tls_certificate_sds_secret_configs" in common
    assert common["tls_certificate_sds_secret_configs"][0]["name"] == "default/my-secret"
    assert "tls_certificates" not in common


@pytest.mark.compilertest
def test_add_context_sds_server_cert_missing_file_paths():
    """SDS mode: no SDS cert config when cert/key file paths are absent (secret not resolved)."""
    ir_ctx = MockIRTLSContext(
        use_sds=True,
        secret_info={
            "sds_cert_name": "default/my-secret",
            # cert_chain_file and private_key_file intentionally absent
        },
    )

    ctx = V3TLSContext()
    ctx.add_context(ir_ctx)

    assert "tls_certificate_sds_secret_configs" not in ctx.get_common()


@pytest.mark.compilertest
def test_add_context_sds_mtls_ca_secret():
    """SDS mode: CA cert (ca_secret) produces validation_context_sds_secret_config."""
    ir_ctx = MockIRTLSContext(
        use_sds=True,
        secret_info={
            "sds_cert_name": "default/server-secret",
            "cert_chain_file": "/path/to/cert",
            "private_key_file": "/path/to/key",
            "sds_cacert_name": "default/ca-secret",
            "cacert_chain_file": "/path/to/ca.crt",
        },
    )

    ctx = V3TLSContext()
    ctx.add_context(ir_ctx)

    common = ctx.get_common()
    assert "validation_context_sds_secret_config" in common
    assert common["validation_context_sds_secret_config"]["name"] == "default/ca-secret"
    assert "validation_context" not in common


@pytest.mark.compilertest
def test_add_context_sds_cacert_chain_file_fallback():
    """SDS mode: cacert_chain_file without sds_cacert_name falls back to file-based validation_context."""
    ir_ctx = MockIRTLSContext(
        use_sds=True,
        secret_info={
            "sds_cert_name": "default/server-secret",
            "cert_chain_file": "/path/to/cert",
            "private_key_file": "/path/to/key",
            "cacert_chain_file": "/path/to/ca.pem",
            # sds_cacert_name intentionally absent
        },
    )

    ctx = V3TLSContext()
    ctx.add_context(ir_ctx)

    common = ctx.get_common()
    assert "validation_context" in common
    assert common["validation_context"]["trusted_ca"] == {"filename": "/path/to/ca.pem"}
    assert "validation_context_sds_secret_config" not in common


# ---------------------------------------------------------------------------
# add_context — file mode
# ---------------------------------------------------------------------------


@pytest.mark.compilertest
def test_add_context_file_mode_server_cert():
    """File mode: cert/key go into tls_certificates, not tls_certificate_sds_secret_configs."""
    ir_ctx = MockIRTLSContext(
        use_sds=False,
        secret_info={
            "cert_chain_file": "/path/to/cert",
            "private_key_file": "/path/to/key",
        },
    )

    ctx = V3TLSContext()
    ctx.add_context(ir_ctx)

    common = ctx.get_common()
    certs = common.get("tls_certificates", [{}])
    assert certs[0]["certificate_chain"] == {"filename": "/path/to/cert"}
    assert certs[0]["private_key"] == {"filename": "/path/to/key"}
    assert "tls_certificate_sds_secret_configs" not in common


@pytest.mark.compilertest
def test_add_context_file_mode_mtls():
    """File mode: CA cert goes into validation_context, not validation_context_sds_secret_config."""
    ir_ctx = MockIRTLSContext(
        use_sds=False,
        secret_info={
            "cert_chain_file": "/path/to/cert",
            "private_key_file": "/path/to/key",
            "cacert_chain_file": "/path/to/ca.pem",
        },
    )

    ctx = V3TLSContext()
    ctx.add_context(ir_ctx)

    common = ctx.get_common()
    assert common["validation_context"]["trusted_ca"] == {"filename": "/path/to/ca.pem"}
    assert "validation_context_sds_secret_config" not in common


# ---------------------------------------------------------------------------
# add_context — common TLS parameters (mode-independent)
# ---------------------------------------------------------------------------


@pytest.mark.compilertest
def test_add_context_cert_required():
    """cert_required maps to require_client_certificate on the top-level context."""
    ir_ctx = MockIRTLSContext(use_sds=False, secret_info={})
    ir_ctx["cert_required"] = True

    ctx = V3TLSContext()
    ctx.add_context(ir_ctx)

    assert ctx.get("require_client_certificate") is True


@pytest.mark.compilertest
def test_add_context_tls_versions():
    """min/max TLS versions are mapped to Envoy's version identifiers."""
    ir_ctx = MockIRTLSContext(use_sds=False, secret_info={})
    ir_ctx["min_tls_version"] = "v1.2"
    ir_ctx["max_tls_version"] = "v1.3"

    ctx = V3TLSContext()
    ctx.add_context(ir_ctx)

    params = ctx.get_params()
    assert params["tls_minimum_protocol_version"] == "TLSv1_2"
    assert params["tls_maximum_protocol_version"] == "TLSv1_3"


@pytest.mark.compilertest
def test_add_context_fallback_flag():
    """is_fallback is propagated from the IR context."""
    ir_ctx = MockIRTLSContext(use_sds=False, secret_info={}, is_fallback=True)

    ctx = V3TLSContext()
    ctx.add_context(ir_ctx)

    assert ctx.is_fallback is True


@pytest.mark.compilertest
def test_add_context_sni():
    """sni is set on the top-level context."""
    ir_ctx = MockIRTLSContext(use_sds=False, secret_info={})
    ir_ctx["sni"] = "example.com"

    ctx = V3TLSContext()
    ctx.add_context(ir_ctx)

    assert ctx.get("sni") == "example.com"
