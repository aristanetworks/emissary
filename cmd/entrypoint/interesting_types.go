package entrypoint

import (
	"context"
	"fmt"

	"github.com/datawire/dlib/dlog"
	"github.com/emissary-ingress/emissary/v3/pkg/kates"
)

// thingToWatch is... uh... a thing we're gonna watch. Specifically, it's a
// K8s type name and an optional field selector.
type thingToWatch struct {
	typename      string
	fieldselector string
}

type thingToMaybeWatch struct {
	typename      string
	fieldselector string
	ignoreIf      bool
}

// GetQueries takes a set of interesting types, and returns a set of kates.Query to watch
// for them.
func GetQueries(ctx context.Context, interestingTypes map[string]thingToWatch) []kates.Query {
	ns := kates.NamespaceAll
	if IsAmbassadorSingleNamespace() {
		ns = GetAmbassadorNamespace()
	}

	fs := GetAmbassadorFieldSelector()
	ls := GetAmbassadorLabelSelector()

	var queries []kates.Query
	for snapshotname, queryinfo := range interestingTypes {
		query := kates.Query{
			Namespace:     ns,
			Name:          snapshotname,
			Kind:          queryinfo.typename,
			FieldSelector: queryinfo.fieldselector,
			LabelSelector: ls,
		}
		if query.FieldSelector == "" {
			query.FieldSelector = fs
		}

		queries = append(queries, query)
		dlog.Debugf(ctx, "WATCHER: watching %#v", query)
	}

	return queries
}

// GetInterestingTypes takes a list of available server types, and returns the types we think
// are interesting to watch.
func GetInterestingTypes(ctx context.Context, serverTypeList []kates.APIResource) map[string]thingToWatch {
	fs := GetAmbassadorFieldSelector()
	endpointFs := "metadata.namespace!=kube-system"
	if fs != "" {
		endpointFs += fmt.Sprintf(",%s", fs)
	}

	// We set interestingTypes to the list of types that we'd like to watch (if that type exits
	// in this cluster).
	//
	// - The key in the map is the how we'll label them in the snapshot we pass to the rest of
	//   Ambassador.
	// - The map values are a list, of potential things to watch (based on which of them exist),
	//   ordered from lowest-priority to highest-priority.
	// - The typename in the map values should be the qualified "${name}.${version}.${group}",
	//   where "${name} is lowercase+plural.
	// - If the map value doesn't set a field selector, then `fs` (above) will be used.
	interestingTypes := map[string][]thingToMaybeWatch{
		// Native Kubernetes types
		//
		// Note that we pull `secrets.v1.` in to "K8sSecrets".  ReconcileSecrets will pull
		// over the ones we need into "Secrets" and "Endpoints" respectively.
		"Services":       {{typename: "services.v1."}},                             // New in Kubernetes 0.16.0 (2015-04-28) (v1beta{1..3} before that)
		"Endpoints":      {{typename: "endpoints.v1.", fieldselector: endpointFs}}, // New in Kubernetes 0.16.0 (2015-04-28) (v1beta{1..3} before that)
		"EndpointSlices": {{typename: "endpointslices.v1.discovery.k8s.io", fieldselector: endpointFs}},
		"K8sSecrets":     {{typename: "secrets.v1."}}, // New in Kubernetes 0.16.0 (2015-04-28) (v1beta{1..3} before that)

		// Native Emissary types
		"AuthServices":                {{typename: "authservices.v3alpha1.getambassador.io"}},
		"DevPortals":                  {{typename: "devportals.v3alpha1.getambassador.io"}},
		"Hosts":                       {{typename: "hosts.v3alpha1.getambassador.io"}},
		"KubernetesEndpointResolvers": {{typename: "kubernetesendpointresolvers.v3alpha1.getambassador.io"}},
		"KubernetesServiceResolvers":  {{typename: "kubernetesserviceresolvers.v3alpha1.getambassador.io"}},
		"Listeners":                   {{typename: "listeners.v3alpha1.getambassador.io"}},
		"LogServices":                 {{typename: "logservices.v3alpha1.getambassador.io"}},
		"Mappings":                    {{typename: "mappings.v3alpha1.getambassador.io"}},
		"Modules":                     {{typename: "modules.v3alpha1.getambassador.io"}},
		"RateLimitServices":           {{typename: "ratelimitservices.v3alpha1.getambassador.io"}},
		"TCPMappings":                 {{typename: "tcpmappings.v3alpha1.getambassador.io"}},
		"TLSContexts":                 {{typename: "tlscontexts.v3alpha1.getambassador.io"}},
		"TracingServices":             {{typename: "tracingservices.v3alpha1.getambassador.io"}},
	}

	var serverTypes map[string]kates.APIResource
	if serverTypeList != nil {
		serverTypes = make(map[string]kates.APIResource, len(serverTypeList))
		for _, typeinfo := range serverTypeList {
			serverTypes[typeinfo.Name+"."+typeinfo.Version+"."+typeinfo.Group] = typeinfo
		}
	}

	ret := make(map[string]thingToWatch)
	for k, queryinfos := range interestingTypes {
		var last thingToWatch
		for _, queryinfo := range queryinfos {
			if queryinfo.ignoreIf {
				continue
			}
			last = thingToWatch{queryinfo.typename, queryinfo.fieldselector}
			if _, haveType := serverTypes[queryinfo.typename]; haveType || serverTypes == nil {
				ret[k] = last
			}
		}
		if _, found := ret[k]; !found && last != (thingToWatch{}) {
			dlog.Warnf(ctx, "Warning, unable to watch %s, unknown kind.", last.typename)
		}
	}

	return ret
}
