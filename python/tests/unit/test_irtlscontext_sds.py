"""
Tests for IRTLSContext SDS (Secret Discovery Service) behavior.

These tests verify that resolve() correctly populates sds_cert_name,
sds_cacert_name, etc. in secret_info when AMBASSADOR_ENABLE_SDS is set,
and that those names follow the "{namespace}/{secret_name}" format.
"""
import logging
from unittest.mock import patch

import pytest

from ambassador import IR, Config
from ambassador.fetch import ResourceFetcher
from ambassador.utils import NullSecretHandler
from tests.utils import default_listener_manifests

logger = logging.getLogger("test_irtlscontext_sds")


def _build_ir(yaml: str) -> IR:
    aconf = Config()
    fetcher = ResourceFetcher(logger, aconf)
    fetcher.parse_yaml(yaml, k8s=True)
    aconf.load_all(fetcher.sorted())
    # NullSecretHandler returns a fake SecretInfo for any secret name, which is
    # enough for resolve() to succeed and populate secret_info paths and SDS names.
    secret_handler = NullSecretHandler(logger, None, None, "0")
    ir = IR(aconf, logger=logger, file_checker=lambda path: True, secret_handler=secret_handler)
    assert ir
    return ir


def _tlscontext_yaml(spec_yaml: str) -> str:
    return default_listener_manifests() + spec_yaml


_TLSCONTEXT_SERVER_ONLY = _tlscontext_yaml("""
---
apiVersion: getambassador.io/v3alpha1
kind: TLSContext
metadata:
  name: server-tls
  namespace: default
spec:
  secret: my-tls-secret
  hosts:
  - "*.example.com"
""")

_TLSCONTEXT_WITH_CA_SECRET = _tlscontext_yaml("""
---
apiVersion: getambassador.io/v3alpha1
kind: TLSContext
metadata:
  name: server-tls-mtls
  namespace: default
spec:
  secret: my-tls-secret
  ca_secret: my-ca-secret
  cert_required: true
  hosts:
  - "*.example.com"
""")

_TLSCONTEXT_CROSS_NAMESPACE = _tlscontext_yaml("""
---
apiVersion: getambassador.io/v3alpha1
kind: TLSContext
metadata:
  name: cross-ns-tls
  namespace: default
spec:
  secret: my-tls-secret.other-namespace
  hosts:
  - "*.example.com"
""")


# ---------------------------------------------------------------------------
# SDS disabled (default)
# ---------------------------------------------------------------------------


@pytest.mark.compilertest
def test_no_sds_names_when_sds_disabled():
    """When SDS is disabled, secret_info must not contain any sds_* keys."""
    ir = _build_ir(_TLSCONTEXT_SERVER_ONLY)

    ctx = ir.get_tls_context("server-tls")
    assert ctx is not None

    secret_info = ctx.secret_info
    assert "sds_cert_name" not in secret_info
    assert "sds_key_name" not in secret_info
    assert "sds_cacert_name" not in secret_info

    # File paths should still be set
    assert "cert_chain_file" in secret_info
    assert "private_key_file" in secret_info


# ---------------------------------------------------------------------------
# SDS enabled — server cert
# ---------------------------------------------------------------------------


@pytest.mark.compilertest
@patch.dict("os.environ", {"AMBASSADOR_ENABLE_SDS": "true"})
def test_sds_cert_name_set_on_server_secret():
    """With SDS enabled, sds_cert_name is set to '{namespace}/{secret_name}'."""
    ir = _build_ir(_TLSCONTEXT_SERVER_ONLY)

    ctx = ir.get_tls_context("server-tls")
    assert ctx is not None
    assert ctx.use_sds is True

    secret_info = ctx.secret_info
    assert secret_info.get("sds_cert_name") == "default/my-tls-secret"
    assert secret_info.get("sds_key_name") == "default/my-tls-secret"
    assert secret_info.get("sds_namespace") == "default"


@pytest.mark.compilertest
@patch.dict("os.environ", {"AMBASSADOR_ENABLE_SDS": "true"})
def test_sds_cert_name_file_paths_also_set():
    """With SDS enabled, file paths are still set (used as resolved-secret proof)."""
    ir = _build_ir(_TLSCONTEXT_SERVER_ONLY)

    ctx = ir.get_tls_context("server-tls")
    assert ctx is not None

    secret_info = ctx.secret_info
    assert secret_info.get("cert_chain_file") is not None
    assert secret_info.get("private_key_file") is not None


# ---------------------------------------------------------------------------
# SDS enabled — CA cert (mTLS)
# ---------------------------------------------------------------------------


@pytest.mark.compilertest
@patch.dict("os.environ", {"AMBASSADOR_ENABLE_SDS": "true"})
def test_sds_cacert_name_set_on_ca_secret():
    """With SDS enabled, sds_cacert_name is set to '{namespace}/{ca_secret_name}'."""
    ir = _build_ir(_TLSCONTEXT_WITH_CA_SECRET)

    ctx = ir.get_tls_context("server-tls-mtls")
    assert ctx is not None

    secret_info = ctx.secret_info
    assert secret_info.get("sds_cacert_name") == "default/my-ca-secret"


@pytest.mark.compilertest
@patch.dict("os.environ", {"AMBASSADOR_ENABLE_SDS": "true"})
def test_sds_cacert_file_path_also_set():
    """With SDS enabled, cacert_chain_file is still set alongside sds_cacert_name."""
    ir = _build_ir(_TLSCONTEXT_WITH_CA_SECRET)

    ctx = ir.get_tls_context("server-tls-mtls")
    assert ctx is not None

    assert ctx.secret_info.get("cacert_chain_file") is not None


@pytest.mark.compilertest
@patch.dict("os.environ", {"AMBASSADOR_ENABLE_SDS": "false"})
def test_no_sds_cacert_name_when_sds_disabled():
    """With SDS disabled, sds_cacert_name must not be set even if ca_secret is given."""
    ir = _build_ir(_TLSCONTEXT_WITH_CA_SECRET)

    ctx = ir.get_tls_context("server-tls-mtls")
    assert ctx is not None

    assert "sds_cacert_name" not in ctx.secret_info


# ---------------------------------------------------------------------------
# SDS enabled — cross-namespace secret reference
# ---------------------------------------------------------------------------


@pytest.mark.compilertest
@patch.dict("os.environ", {"AMBASSADOR_ENABLE_SDS": "true"})
def test_sds_cert_name_cross_namespace():
    """Namespace separator in secret name is reflected in the SDS resource name."""
    ir = _build_ir(_TLSCONTEXT_CROSS_NAMESPACE)

    ctx = ir.get_tls_context("cross-ns-tls")
    assert ctx is not None

    # The secret "my-tls-secret.other-namespace" resolves to namespace "other-namespace"
    assert ctx.secret_info.get("sds_cert_name") == "other-namespace/my-tls-secret"
    assert ctx.secret_info.get("sds_namespace") == "other-namespace"
