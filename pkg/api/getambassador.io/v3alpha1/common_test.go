package v3alpha1_test

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"sigs.k8s.io/yaml"

	crds "github.com/emissary-ingress/emissary/v3/pkg/api/getambassador.io/v3alpha1"
)

func TestAmbassadorID(t *testing.T) {
	t.Parallel()
	type subtest struct {
		inputResource crds.AmbassadorID
		inputEnvVar   string
		expected      bool
	}
	subtests := map[string]subtest{
		"nil-d":   {crds.AmbassadorID(nil), "default", true},
		"nil-c":   {crds.AmbassadorID(nil), "custom", false},
		"empty-d": {crds.AmbassadorID{}, "default", true},
		"empty-c": {crds.AmbassadorID{}, "custom", false},
		"one-d":   {crds.AmbassadorID{"default"}, "default", true},
		"one-c":   {crds.AmbassadorID{"default"}, "custom", false},
		"one-c2":  {crds.AmbassadorID{"custom"}, "custom", true},
		"multi":   {crds.AmbassadorID{"default", "custom"}, "custom", true},
	}
	for name, info := range subtests {
		info := info // capture loop variable
		t.Run(name, func(t *testing.T) {
			t.Parallel()
			assert.Equal(t, info.expected, info.inputResource.Matches(info.inputEnvVar))
		})
	}
}

func TestMillisecondDuration(t *testing.T) {
	t.Parallel()
	type TestResource struct {
		Field crds.MillisecondDuration `json:"field,omitempty"`
	}
	type subtest struct {
		inputYAML      string
		expectedStruct TestResource
		expectedJSON   string
		expectedErr    string
	}
	subtests := map[string]subtest{
		"empty":         {`{}`, TestResource{}, `{"field":0}`, ``},
		"explicitEmpty": {`field:`, TestResource{}, `{"field":0}`, ``},
		"explicitnull":  {`field: null`, TestResource{}, `{"field":0}`, ``},
		"explicitNull":  {`field: Null`, TestResource{}, `{"field":0}`, ``},
		"explicitNULL":  {`field: NULL`, TestResource{}, `{"field":0}`, ``},
		"explicitTilde": {`field: ~`, TestResource{}, `{"field":0}`, ``},
		"3000":          {`field: 3000`, TestResource{crds.MillisecondDuration{3 * time.Second}}, `{"field":3000}`, ``},
		"overflow32":    {`field: 4320000000`, TestResource{crds.MillisecondDuration{50 * 24 * time.Hour}}, `{"field":4320000000}`, ``},
		"string":        {`field: "30s"`, TestResource{crds.MillisecondDuration{0}}, `{"field":0}`, "error unmarshaling JSON: while decoding JSON: json: cannot unmarshal string into Go struct field TestResource.field of type int64"},
	}
	for name, info := range subtests {
		info := info // capture loop variable
		t.Run(name, func(t *testing.T) {
			t.Parallel()
			var parsed TestResource
			err := yaml.Unmarshal([]byte(info.inputYAML), &parsed)
			if info.expectedErr == `` {
				assert.NoError(t, err)
			} else {
				assert.EqualError(t, err, info.expectedErr)
			}
			assert.Equal(t, info.expectedStruct, parsed)
			jsonbytes, err := json.Marshal(parsed)
			assert.NoError(t, err)
			assert.Equal(t, info.expectedJSON, string(jsonbytes))
		})
	}
}

func TestMillisecondDurationPtr(t *testing.T) {
	t.Parallel()
	type TestResource struct {
		Field *crds.MillisecondDuration `json:"field,omitempty"`
	}
	type subtest struct {
		inputYAML      string
		expectedStruct TestResource
		expectedJSON   string
		expectedErr    string
	}
	subtests := map[string]subtest{
		"empty":         {`{}`, TestResource{}, `{}`, ``},
		"explicitEmpty": {`field:`, TestResource{}, `{}`, ``},
		"explicitnull":  {`field: null`, TestResource{}, `{}`, ``},
		"explicitNull":  {`field: Null`, TestResource{}, `{}`, ``},
		"explicitNULL":  {`field: NULL`, TestResource{}, `{}`, ``},
		"explicitTilde": {`field: ~`, TestResource{}, `{}`, ``},
		"3000":          {`field: 3000`, TestResource{&crds.MillisecondDuration{3 * time.Second}}, `{"field":3000}`, ``},
		"overflow32":    {`field: 4320000000`, TestResource{&crds.MillisecondDuration{50 * 24 * time.Hour}}, `{"field":4320000000}`, ``},
		"string":        {`field: "30s"`, TestResource{&crds.MillisecondDuration{0}}, `{"field":0}`, "error unmarshaling JSON: while decoding JSON: json: cannot unmarshal string into Go struct field TestResource.field of type int64"},
	}
	for name, info := range subtests {
		info := info // capture loop variable
		t.Run(name, func(t *testing.T) {
			t.Parallel()
			var parsed TestResource
			err := yaml.Unmarshal([]byte(info.inputYAML), &parsed)
			if info.expectedErr == `` {
				assert.NoError(t, err)
			} else {
				assert.EqualError(t, err, info.expectedErr)
			}
			assert.Equal(t, info.expectedStruct, parsed)
			jsonbytes, err := json.Marshal(parsed)
			assert.NoError(t, err)
			assert.Equal(t, info.expectedJSON, string(jsonbytes))
		})
	}
}

func TestUntypedDict(t *testing.T) {
	t.Parallel()
	type TestResource struct {
		Field crds.UntypedDict `json:"field,omitempty"`
	}
	type subtest struct {
		inputYAML      string
		expectedStruct TestResource
		expectedJSON   string
		expectedErr    string
	}
	subtests := map[string]subtest{
		"empty":         {`{}`, TestResource{}, `{"field":null}`, ``},
		"explicitEmpty": {`field:`, TestResource{}, `{"field":null}`, ``},
		"explicitnull":  {`field: null`, TestResource{}, `{"field":null}`, ``},
		"explicitNull":  {`field: Null`, TestResource{}, `{"field":null}`, ``},
		"explicitNULL":  {`field: NULL`, TestResource{}, `{"field":null}`, ``},
		"explicitTilde": {`field: ~`, TestResource{}, `{"field":null}`, ``},
		"basic":         {`field: {foo: "bar"}`, TestResource{crds.UntypedDict{map[string]json.RawMessage{"foo": json.RawMessage(`"bar"`)}}}, `{"field":{"foo":"bar"}}`, ``},
		"string":        {`field: "str"`, TestResource{}, `{"field":null}`, "error unmarshaling JSON: while decoding JSON: json: cannot unmarshal string into Go struct field TestResource.field of type map[string]json.RawMessage"},
		"badkey": {`
badkey: &anchor
  baz: qux
field: { *anchor: "bar"}`, TestResource{}, `{"field":null}`, "error converting YAML to JSON: yaml: invalid map key: map[interface {}]interface {}{\"baz\":\"qux\"}"},
	}
	for name, info := range subtests {
		info := info // capture loop variable
		t.Run(name, func(t *testing.T) {
			t.Parallel()
			var parsed TestResource
			err := yaml.Unmarshal([]byte(info.inputYAML), &parsed)
			if info.expectedErr == `` {
				assert.NoError(t, err)
			} else {
				assert.EqualError(t, err, info.expectedErr)
			}
			assert.Equal(t, info.expectedStruct, parsed)
			jsonbytes, err := json.Marshal(parsed)
			assert.NoError(t, err)
			assert.Equal(t, info.expectedJSON, string(jsonbytes))
		})
	}
}

func TestUntypedDictPtr(t *testing.T) {
	t.Parallel()
	type TestResource struct {
		Field *crds.UntypedDict `json:"field,omitempty"`
	}
	type subtest struct {
		inputYAML      string
		expectedStruct TestResource
		expectedJSON   string
		expectedErr    string
	}
	subtests := map[string]subtest{
		"empty":         {`{}`, TestResource{}, `{}`, ``},
		"explicitEmpty": {`field:`, TestResource{}, `{}`, ``},
		"explicitnull":  {`field: null`, TestResource{}, `{}`, ``},
		"explicitNull":  {`field: Null`, TestResource{}, `{}`, ``},
		"explicitNULL":  {`field: NULL`, TestResource{}, `{}`, ``},
		"explicitTilde": {`field: ~`, TestResource{}, `{}`, ``},
		"basic":         {`field: {foo: "bar"}`, TestResource{&crds.UntypedDict{map[string]json.RawMessage{"foo": json.RawMessage(`"bar"`)}}}, `{"field":{"foo":"bar"}}`, ``},
		"string":        {`field: "str"`, TestResource{&crds.UntypedDict{}}, `{"field":null}`, "error unmarshaling JSON: while decoding JSON: json: cannot unmarshal string into Go struct field TestResource.field of type map[string]json.RawMessage"},
		"badkey": {`
badkey: &anchor
  baz: qux
field: { *anchor: "bar"}`, TestResource{}, `{}`, "error converting YAML to JSON: yaml: invalid map key: map[interface {}]interface {}{\"baz\":\"qux\"}"},
	}
	for name, info := range subtests {
		info := info // capture loop variable
		t.Run(name, func(t *testing.T) {
			t.Parallel()
			var parsed TestResource
			err := yaml.Unmarshal([]byte(info.inputYAML), &parsed)
			if info.expectedErr == `` {
				assert.NoError(t, err)
			} else {
				assert.EqualError(t, err, info.expectedErr)
			}
			assert.Equal(t, info.expectedStruct, parsed)
			jsonbytes, err := json.Marshal(parsed)
			assert.NoError(t, err)
			assert.Equal(t, info.expectedJSON, string(jsonbytes))
		})
	}
}

func TestPercent(t *testing.T) {
	t.Parallel()
	type TestResource struct {
		Field crds.Percent `json:"field,omitempty"`
	}
	type subtest struct {
		inputYAML      string
		expectedStruct TestResource
		expectedJSON   string
		expectedErr    string
	}
	subtests := map[string]subtest{
		"empty":         {`{}`, TestResource{}, `{"field":0}`, ``},
		"explicitEmpty": {`field:`, TestResource{}, `{"field":0}`, ``},
		"explicitnull":  {`field: null`, TestResource{}, `{"field":0}`, ``},
		"explicitNull":  {`field: Null`, TestResource{}, `{"field":0}`, ``},
		"explicitNULL":  {`field: NULL`, TestResource{}, `{"field":0}`, ``},
		"explicitTilde": {`field: ~`, TestResource{}, `{"field":0}`, ``},
		"50.5":          {`field: 50.5`, TestResource{crds.Percent{50.5}}, `{"field":50.5}`, ``},
		"0":             {`field: 0`, TestResource{crds.Percent{0}}, `{"field":0}`, ``},
		"100":           {`field: 100`, TestResource{crds.Percent{100}}, `{"field":100}`, ``},
		"decimal":       {`field: 25.75`, TestResource{crds.Percent{25.75}}, `{"field":25.75}`, ``},
		"string":        {`field: "50%"`, TestResource{crds.Percent{0}}, `{"field":0}`, "error unmarshaling JSON: while decoding JSON: json: cannot unmarshal string into Go struct field TestResource.field of type float64"},
	}
	for name, info := range subtests {
		info := info // capture loop variable
		t.Run(name, func(t *testing.T) {
			t.Parallel()

			t.Run("YAML", func(t *testing.T) {
				var actual TestResource
				err := yaml.Unmarshal([]byte(info.inputYAML), &actual)
				if info.expectedErr == "" {
					assert.NoError(t, err)
					assert.Equal(t, info.expectedStruct, actual)
				} else {
					assert.EqualError(t, err, info.expectedErr)
				}
			})

			if info.expectedErr == "" {
				t.Run("JSON", func(t *testing.T) {
					actualJSON, err := json.Marshal(info.expectedStruct)
					assert.NoError(t, err)
					assert.Equal(t, info.expectedJSON, string(actualJSON))
				})
			}
		})
	}
}
