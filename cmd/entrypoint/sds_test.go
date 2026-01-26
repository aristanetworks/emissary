package entrypoint

import (
	"testing"

	v1 "k8s.io/api/core/v1"

	"github.com/emissary-ingress/emissary/v3/pkg/kates"
)

func TestBuildSDSSecret_TLSCertificate(t *testing.T) {
	secret := &kates.Secret{
		TypeMeta: kates.TypeMeta{Kind: "Secret"},
		ObjectMeta: kates.ObjectMeta{
			Name:      "test-tls-secret",
			Namespace: "default",
		},
		Type: v1.SecretTypeTLS,
		Data: map[string][]byte{
			"tls.crt": []byte("-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----"),
			"tls.key": []byte("-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----"),
		},
	}

	sdsSecret, err := BuildSDSSecret(secret, "default", "test-tls-secret")
	if err != nil {
		t.Fatalf("BuildSDSSecret failed: %v", err)
	}

	expectedName := "default/test-tls-secret"
	if sdsSecret.Name != expectedName {
		t.Errorf("Expected name '%s', got '%s'", expectedName, sdsSecret.Name)
	}

	// Check that it's a TLS certificate (not validation context)
	if sdsSecret.GetTlsCertificate() == nil {
		t.Error("Expected TlsCertificate, got nil")
	}

	tlsCert := sdsSecret.GetTlsCertificate()
	if tlsCert.CertificateChain == nil {
		t.Error("Expected CertificateChain, got nil")
	}
	if tlsCert.PrivateKey == nil {
		t.Error("Expected PrivateKey, got nil")
	}
}

func TestBuildSDSSecret_CACertificate(t *testing.T) {
	// CA cert secret only has tls.crt, no private key
	secret := &kates.Secret{
		TypeMeta: kates.TypeMeta{Kind: "Secret"},
		ObjectMeta: kates.ObjectMeta{
			Name:      "ca-cert",
			Namespace: "emissary",
		},
		Type: v1.SecretTypeOpaque,
		Data: map[string][]byte{
			"tls.crt": []byte("-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----"),
		},
	}

	sdsSecret, err := BuildSDSSecret(secret, "emissary", "ca-cert")
	if err != nil {
		t.Fatalf("BuildSDSSecret failed: %v", err)
	}

	expectedName := "emissary/ca-cert"
	if sdsSecret.Name != expectedName {
		t.Errorf("Expected name '%s', got '%s'", expectedName, sdsSecret.Name)
	}

	// Check that it's a validation context (not TLS certificate)
	if sdsSecret.GetValidationContext() == nil {
		t.Error("Expected ValidationContext, got nil")
	}

	validationCtx := sdsSecret.GetValidationContext()
	if validationCtx.TrustedCa == nil {
		t.Error("Expected TrustedCa, got nil")
	}
}

func TestBuildSDSSecret_CACertificateWithCaCrt(t *testing.T) {
	// CA cert secret with ca.crt key (common format)
	secret := &kates.Secret{
		TypeMeta: kates.TypeMeta{Kind: "Secret"},
		ObjectMeta: kates.ObjectMeta{
			Name:      "my-app-ca",
			Namespace: "default",
		},
		Type: v1.SecretTypeOpaque,
		Data: map[string][]byte{
			"ca.crt": []byte("-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----"),
		},
	}

	sdsSecret, err := BuildSDSSecret(secret, "default", "my-app-ca")
	if err != nil {
		t.Fatalf("BuildSDSSecret failed: %v", err)
	}

	expectedName := "default/my-app-ca"
	if sdsSecret.Name != expectedName {
		t.Errorf("Expected name '%s', got '%s'", expectedName, sdsSecret.Name)
	}

	// Check that it's a validation context (not TLS certificate)
	if sdsSecret.GetValidationContext() == nil {
		t.Error("Expected ValidationContext, got nil")
	}

	validationCtx := sdsSecret.GetValidationContext()
	if validationCtx.TrustedCa == nil {
		t.Error("Expected TrustedCa, got nil")
	}
}

func TestBuildSDSSecret_NilSecret(t *testing.T) {
	_, err := BuildSDSSecret(nil, "default", "test")
	if err == nil {
		t.Error("Expected error for nil secret, got nil")
	}
}

func TestBuildSDSSecret_InvalidSecret(t *testing.T) {
	// Secret with no TLS data
	secret := &kates.Secret{
		TypeMeta: kates.TypeMeta{Kind: "Secret"},
		ObjectMeta: kates.ObjectMeta{
			Name:      "invalid-secret",
			Namespace: "default",
		},
		Type: v1.SecretTypeOpaque,
		Data: map[string][]byte{
			"random": []byte("data"),
		},
	}

	_, err := BuildSDSSecret(secret, "default", "invalid-secret")
	if err == nil {
		t.Error("Expected error for invalid secret, got nil")
	}
}

func TestSecretNameToSDS(t *testing.T) {
	tests := []struct {
		namespace string
		name      string
		expected  string
	}{
		{"default", "my-secret", "default/my-secret"},
		{"emissary", "tls-cert", "emissary/tls-cert"},
		{"istio-system", "ingress-cert", "istio-system/ingress-cert"},
	}

	for _, tt := range tests {
		result := SecretNameToSDS(tt.namespace, tt.name)
		if result != tt.expected {
			t.Errorf("SecretNameToSDS(%s, %s) = %s, expected %s",
				tt.namespace, tt.name, result, tt.expected)
		}
	}
}

func TestBuildSDSSecret_MultipleNamespaces(t *testing.T) {
	namespaces := []string{"default", "emissary", "istio-system", "my-app"}

	for _, ns := range namespaces {
		secret := &kates.Secret{
			TypeMeta: kates.TypeMeta{Kind: "Secret"},
			ObjectMeta: kates.ObjectMeta{
				Name:      "tls-secret",
				Namespace: ns,
			},
			Type: v1.SecretTypeTLS,
			Data: map[string][]byte{
				"tls.crt": []byte("cert"),
				"tls.key": []byte("key"),
			},
		}

		sdsSecret, err := BuildSDSSecret(secret, ns, "tls-secret")
		if err != nil {
			t.Fatalf("BuildSDSSecret failed for namespace %s: %v", ns, err)
		}

		expectedName := ns + "/tls-secret"
		if sdsSecret.Name != expectedName {
			t.Errorf("Expected name '%s', got '%s'", expectedName, sdsSecret.Name)
		}
	}
}
