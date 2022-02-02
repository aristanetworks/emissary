// Code generated by protoc-gen-validate. DO NOT EDIT.
// source: envoy/service/load_stats/v2/lrs.proto

package load_statsv2

import (
	"bytes"
	"errors"
	"fmt"
	"net"
	"net/mail"
	"net/url"
	"regexp"
	"sort"
	"strings"
	"time"
	"unicode/utf8"

	"google.golang.org/protobuf/types/known/anypb"
)

// ensure the imports are used
var (
	_ = bytes.MinRead
	_ = errors.New("")
	_ = fmt.Print
	_ = utf8.UTFMax
	_ = (*regexp.Regexp)(nil)
	_ = (*strings.Reader)(nil)
	_ = net.IPv4len
	_ = time.Duration(0)
	_ = (*url.URL)(nil)
	_ = (*mail.Address)(nil)
	_ = anypb.Any{}
	_ = sort.Sort
)

// Validate checks the field values on LoadStatsRequest with the rules defined
// in the proto definition for this message. If any rules are violated, the
// first error encountered is returned, or nil if there are no violations.
func (m *LoadStatsRequest) Validate() error {
	return m.validate(false)
}

// ValidateAll checks the field values on LoadStatsRequest with the rules
// defined in the proto definition for this message. If any rules are
// violated, the result is a list of violation errors wrapped in
// LoadStatsRequestMultiError, or nil if none found.
func (m *LoadStatsRequest) ValidateAll() error {
	return m.validate(true)
}

func (m *LoadStatsRequest) validate(all bool) error {
	if m == nil {
		return nil
	}

	var errors []error

	if all {
		switch v := interface{}(m.GetNode()).(type) {
		case interface{ ValidateAll() error }:
			if err := v.ValidateAll(); err != nil {
				errors = append(errors, LoadStatsRequestValidationError{
					field:  "Node",
					reason: "embedded message failed validation",
					cause:  err,
				})
			}
		case interface{ Validate() error }:
			if err := v.Validate(); err != nil {
				errors = append(errors, LoadStatsRequestValidationError{
					field:  "Node",
					reason: "embedded message failed validation",
					cause:  err,
				})
			}
		}
	} else if v, ok := interface{}(m.GetNode()).(interface{ Validate() error }); ok {
		if err := v.Validate(); err != nil {
			return LoadStatsRequestValidationError{
				field:  "Node",
				reason: "embedded message failed validation",
				cause:  err,
			}
		}
	}

	for idx, item := range m.GetClusterStats() {
		_, _ = idx, item

		if all {
			switch v := interface{}(item).(type) {
			case interface{ ValidateAll() error }:
				if err := v.ValidateAll(); err != nil {
					errors = append(errors, LoadStatsRequestValidationError{
						field:  fmt.Sprintf("ClusterStats[%v]", idx),
						reason: "embedded message failed validation",
						cause:  err,
					})
				}
			case interface{ Validate() error }:
				if err := v.Validate(); err != nil {
					errors = append(errors, LoadStatsRequestValidationError{
						field:  fmt.Sprintf("ClusterStats[%v]", idx),
						reason: "embedded message failed validation",
						cause:  err,
					})
				}
			}
		} else if v, ok := interface{}(item).(interface{ Validate() error }); ok {
			if err := v.Validate(); err != nil {
				return LoadStatsRequestValidationError{
					field:  fmt.Sprintf("ClusterStats[%v]", idx),
					reason: "embedded message failed validation",
					cause:  err,
				}
			}
		}

	}

	if len(errors) > 0 {
		return LoadStatsRequestMultiError(errors)
	}
	return nil
}

// LoadStatsRequestMultiError is an error wrapping multiple validation errors
// returned by LoadStatsRequest.ValidateAll() if the designated constraints
// aren't met.
type LoadStatsRequestMultiError []error

// Error returns a concatenation of all the error messages it wraps.
func (m LoadStatsRequestMultiError) Error() string {
	var msgs []string
	for _, err := range m {
		msgs = append(msgs, err.Error())
	}
	return strings.Join(msgs, "; ")
}

// AllErrors returns a list of validation violation errors.
func (m LoadStatsRequestMultiError) AllErrors() []error { return m }

// LoadStatsRequestValidationError is the validation error returned by
// LoadStatsRequest.Validate if the designated constraints aren't met.
type LoadStatsRequestValidationError struct {
	field  string
	reason string
	cause  error
	key    bool
}

// Field function returns field value.
func (e LoadStatsRequestValidationError) Field() string { return e.field }

// Reason function returns reason value.
func (e LoadStatsRequestValidationError) Reason() string { return e.reason }

// Cause function returns cause value.
func (e LoadStatsRequestValidationError) Cause() error { return e.cause }

// Key function returns key value.
func (e LoadStatsRequestValidationError) Key() bool { return e.key }

// ErrorName returns error name.
func (e LoadStatsRequestValidationError) ErrorName() string { return "LoadStatsRequestValidationError" }

// Error satisfies the builtin error interface
func (e LoadStatsRequestValidationError) Error() string {
	cause := ""
	if e.cause != nil {
		cause = fmt.Sprintf(" | caused by: %v", e.cause)
	}

	key := ""
	if e.key {
		key = "key for "
	}

	return fmt.Sprintf(
		"invalid %sLoadStatsRequest.%s: %s%s",
		key,
		e.field,
		e.reason,
		cause)
}

var _ error = LoadStatsRequestValidationError{}

var _ interface {
	Field() string
	Reason() string
	Key() bool
	Cause() error
	ErrorName() string
} = LoadStatsRequestValidationError{}

// Validate checks the field values on LoadStatsResponse with the rules defined
// in the proto definition for this message. If any rules are violated, the
// first error encountered is returned, or nil if there are no violations.
func (m *LoadStatsResponse) Validate() error {
	return m.validate(false)
}

// ValidateAll checks the field values on LoadStatsResponse with the rules
// defined in the proto definition for this message. If any rules are
// violated, the result is a list of violation errors wrapped in
// LoadStatsResponseMultiError, or nil if none found.
func (m *LoadStatsResponse) ValidateAll() error {
	return m.validate(true)
}

func (m *LoadStatsResponse) validate(all bool) error {
	if m == nil {
		return nil
	}

	var errors []error

	// no validation rules for SendAllClusters

	if all {
		switch v := interface{}(m.GetLoadReportingInterval()).(type) {
		case interface{ ValidateAll() error }:
			if err := v.ValidateAll(); err != nil {
				errors = append(errors, LoadStatsResponseValidationError{
					field:  "LoadReportingInterval",
					reason: "embedded message failed validation",
					cause:  err,
				})
			}
		case interface{ Validate() error }:
			if err := v.Validate(); err != nil {
				errors = append(errors, LoadStatsResponseValidationError{
					field:  "LoadReportingInterval",
					reason: "embedded message failed validation",
					cause:  err,
				})
			}
		}
	} else if v, ok := interface{}(m.GetLoadReportingInterval()).(interface{ Validate() error }); ok {
		if err := v.Validate(); err != nil {
			return LoadStatsResponseValidationError{
				field:  "LoadReportingInterval",
				reason: "embedded message failed validation",
				cause:  err,
			}
		}
	}

	// no validation rules for ReportEndpointGranularity

	if len(errors) > 0 {
		return LoadStatsResponseMultiError(errors)
	}
	return nil
}

// LoadStatsResponseMultiError is an error wrapping multiple validation errors
// returned by LoadStatsResponse.ValidateAll() if the designated constraints
// aren't met.
type LoadStatsResponseMultiError []error

// Error returns a concatenation of all the error messages it wraps.
func (m LoadStatsResponseMultiError) Error() string {
	var msgs []string
	for _, err := range m {
		msgs = append(msgs, err.Error())
	}
	return strings.Join(msgs, "; ")
}

// AllErrors returns a list of validation violation errors.
func (m LoadStatsResponseMultiError) AllErrors() []error { return m }

// LoadStatsResponseValidationError is the validation error returned by
// LoadStatsResponse.Validate if the designated constraints aren't met.
type LoadStatsResponseValidationError struct {
	field  string
	reason string
	cause  error
	key    bool
}

// Field function returns field value.
func (e LoadStatsResponseValidationError) Field() string { return e.field }

// Reason function returns reason value.
func (e LoadStatsResponseValidationError) Reason() string { return e.reason }

// Cause function returns cause value.
func (e LoadStatsResponseValidationError) Cause() error { return e.cause }

// Key function returns key value.
func (e LoadStatsResponseValidationError) Key() bool { return e.key }

// ErrorName returns error name.
func (e LoadStatsResponseValidationError) ErrorName() string {
	return "LoadStatsResponseValidationError"
}

// Error satisfies the builtin error interface
func (e LoadStatsResponseValidationError) Error() string {
	cause := ""
	if e.cause != nil {
		cause = fmt.Sprintf(" | caused by: %v", e.cause)
	}

	key := ""
	if e.key {
		key = "key for "
	}

	return fmt.Sprintf(
		"invalid %sLoadStatsResponse.%s: %s%s",
		key,
		e.field,
		e.reason,
		cause)
}

var _ error = LoadStatsResponseValidationError{}

var _ interface {
	Field() string
	Reason() string
	Key() bool
	Cause() error
	ErrorName() string
} = LoadStatsResponseValidationError{}
