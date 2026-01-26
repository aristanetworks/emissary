package ambex

import (
	ecp_v3_cache "github.com/emissary-ingress/emissary/v3/pkg/envoy-control-plane/cache/v3"
	v3tls "github.com/emissary-ingress/emissary/v3/pkg/api/envoy/extensions/transport_sockets/tls/v3"
)

// FastpathSnapshot holds envoy configuration that bypasses python.
type FastpathSnapshot struct {
	Snapshot  *ecp_v3_cache.Snapshot
	Endpoints *Endpoints
	Secrets   map[string]*v3tls.Secret
}
