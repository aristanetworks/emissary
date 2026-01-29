package kates

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	amb "github.com/emissary-ingress/emissary/v3/pkg/api/getambassador.io/v3alpha1"
)

func TestMergeUpdate(t *testing.T) {
	a := &Unstructured{}
	a.Object = map[string]interface{}{
		"apiVersion": "vtest",
		"kind":       "Foo",
		"metadata": map[string]interface{}{
			"name":            "foo",
			"namespace":       "default",
			"resourceVersion": "1234",
			"labels": map[string]interface{}{
				"foo": "bar",
			},
			"annotations": map[string]interface{}{
				"moo": "arf",
			},
		},
		"spec": map[string]interface{}{
			"foo": "bar",
		},
	}

	b := &Unstructured{}
	b.Object = map[string]interface{}{
		"apiVersion": "vtest",
		"kind":       "Foo",
		"metadata": map[string]interface{}{
			"labels": map[string]interface{}{
				"foo": "bar",
				"moo": "arf",
			},
			"annotations": map[string]interface{}{
				"foo": "bar",
				"moo": "arf",
			},
		},
		"spec": map[string]interface{}{
			"key": "value",
		},
	}

	assert.NotEqual(t, a.Object["spec"], b.Object["spec"])

	MergeUpdate(a, b)

	assert.Equal(t, "arf", a.GetLabels()["moo"])
	assert.Equal(t, "bar", a.GetAnnotations()["foo"])
	assert.Equal(t, b.Object["spec"], a.Object["spec"])
}

const mapping = `---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name:  mapping-name
spec:
  prefix: /mapping-prefix/
  service: http://mapping-service
`

func TestParseManifestsResultTypes(t *testing.T) {
	objs, err := ParseManifests(mapping)
	require.NoError(t, err)
	require.Equal(t, 1, len(objs))

	m := objs[0]
	t.Logf("value = %v", m)
	t.Logf("type = %T", m)
	_, ok := m.(*amb.Mapping)
	require.True(t, ok)
}
