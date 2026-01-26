package entrypoint

import (
	"fmt"

	v1 "k8s.io/api/core/v1"

	v3core "github.com/emissary-ingress/emissary/v3/pkg/api/envoy/config/core/v3"
	v3tls "github.com/emissary-ingress/emissary/v3/pkg/api/envoy/extensions/transport_sockets/tls/v3"
	"github.com/emissary-ingress/emissary/v3/pkg/kates"
)

// BuildSDSSecret converts a Kubernetes secret to an Envoy Secret proto for SDS.
// The secret name will be in the format "{namespace}/{name}".
func BuildSDSSecret(secret *kates.Secret, namespace, name string) (*v3tls.Secret, error) {
	if secret == nil {
		return nil, fmt.Errorf("secret is nil")
	}

	// Create the SDS secret name in the format "namespace/name"
	sdsName := SecretNameToSDS(namespace, name)

	// Determine secret type and build appropriate Secret proto
	secretType := secret.Type
	if secretType == "" {
		secretType = v1.SecretTypeOpaque
	}

	var tlsSecret *v3tls.Secret

	switch secretType {
	case v1.SecretTypeTLS, v1.SecretTypeOpaque:
		// Handle TLS certificates (server certs)
		certData, certExists := secret.Data["tls.crt"]
		keyData, keyExists := secret.Data["tls.key"]
		// Also check for ca.crt (common for CA certificates)
		caCertData, caCertExists := secret.Data["ca.crt"]

		if certExists && keyExists {
			// This is a TLS certificate with both cert and key
			tlsSecret = &v3tls.Secret{
				Name: sdsName,
				Type: &v3tls.Secret_TlsCertificate{
					TlsCertificate: &v3tls.TlsCertificate{
						CertificateChain: &v3core.DataSource{
							Specifier: &v3core.DataSource_InlineBytes{
								InlineBytes: certData,
							},
						},
						PrivateKey: &v3core.DataSource{
							Specifier: &v3core.DataSource_InlineBytes{
								InlineBytes: keyData,
							},
						},
					},
				},
			}
		} else if certExists {
			// This is a CA certificate (validation context) with tls.crt
			tlsSecret = &v3tls.Secret{
				Name: sdsName,
				Type: &v3tls.Secret_ValidationContext{
					ValidationContext: &v3tls.CertificateValidationContext{
						TrustedCa: &v3core.DataSource{
							Specifier: &v3core.DataSource_InlineBytes{
								InlineBytes: certData,
							},
						},
					},
				},
			}
		} else if caCertExists {
			// This is a CA certificate (validation context) with ca.crt
			tlsSecret = &v3tls.Secret{
				Name: sdsName,
				Type: &v3tls.Secret_ValidationContext{
					ValidationContext: &v3tls.CertificateValidationContext{
						TrustedCa: &v3core.DataSource{
							Specifier: &v3core.DataSource_InlineBytes{
								InlineBytes: caCertData,
							},
						},
					},
				},
			}
		} else {
			return nil, fmt.Errorf("secret %s/%s does not contain valid TLS data (no tls.crt, tls.key, or ca.crt)", namespace, name)
		}

	default:
		return nil, fmt.Errorf("unsupported secret type %s for secret %s/%s", secretType, namespace, name)
	}

	return tlsSecret, nil
}

// SecretNameToSDS converts a namespace and secret name to an SDS resource name.
// Format: "{namespace}/{name}"
func SecretNameToSDS(namespace, name string) string {
	return fmt.Sprintf("%s/%s", namespace, name)
}
