// Code generated by protoc-gen-validate. DO NOT EDIT.
// source: envoy/api/v2/endpoint.proto

package apiv2

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

// Validate checks the field values on ClusterLoadAssignment with the rules
// defined in the proto definition for this message. If any rules are
// violated, the first error encountered is returned, or nil if there are no violations.
func (m *ClusterLoadAssignment) Validate() error {
	return m.validate(false)
}

// ValidateAll checks the field values on ClusterLoadAssignment with the rules
// defined in the proto definition for this message. If any rules are
// violated, the result is a list of violation errors wrapped in
// ClusterLoadAssignmentMultiError, or nil if none found.
func (m *ClusterLoadAssignment) ValidateAll() error {
	return m.validate(true)
}

func (m *ClusterLoadAssignment) validate(all bool) error {
	if m == nil {
		return nil
	}

	var errors []error

	if len(m.GetClusterName()) < 1 {
		err := ClusterLoadAssignmentValidationError{
			field:  "ClusterName",
			reason: "value length must be at least 1 bytes",
		}
		if !all {
			return err
		}
		errors = append(errors, err)
	}

	for idx, item := range m.GetEndpoints() {
		_, _ = idx, item

		if all {
			switch v := interface{}(item).(type) {
			case interface{ ValidateAll() error }:
				if err := v.ValidateAll(); err != nil {
					errors = append(errors, ClusterLoadAssignmentValidationError{
						field:  fmt.Sprintf("Endpoints[%v]", idx),
						reason: "embedded message failed validation",
						cause:  err,
					})
				}
			case interface{ Validate() error }:
				if err := v.Validate(); err != nil {
					errors = append(errors, ClusterLoadAssignmentValidationError{
						field:  fmt.Sprintf("Endpoints[%v]", idx),
						reason: "embedded message failed validation",
						cause:  err,
					})
				}
			}
		} else if v, ok := interface{}(item).(interface{ Validate() error }); ok {
			if err := v.Validate(); err != nil {
				return ClusterLoadAssignmentValidationError{
					field:  fmt.Sprintf("Endpoints[%v]", idx),
					reason: "embedded message failed validation",
					cause:  err,
				}
			}
		}

	}

	{
		sorted_keys := make([]string, len(m.GetNamedEndpoints()))
		i := 0
		for key := range m.GetNamedEndpoints() {
			sorted_keys[i] = key
			i++
		}
		sort.Slice(sorted_keys, func(i, j int) bool { return sorted_keys[i] < sorted_keys[j] })
		for _, key := range sorted_keys {
			val := m.GetNamedEndpoints()[key]
			_ = val

			// no validation rules for NamedEndpoints[key]

			if all {
				switch v := interface{}(val).(type) {
				case interface{ ValidateAll() error }:
					if err := v.ValidateAll(); err != nil {
						errors = append(errors, ClusterLoadAssignmentValidationError{
							field:  fmt.Sprintf("NamedEndpoints[%v]", key),
							reason: "embedded message failed validation",
							cause:  err,
						})
					}
				case interface{ Validate() error }:
					if err := v.Validate(); err != nil {
						errors = append(errors, ClusterLoadAssignmentValidationError{
							field:  fmt.Sprintf("NamedEndpoints[%v]", key),
							reason: "embedded message failed validation",
							cause:  err,
						})
					}
				}
			} else if v, ok := interface{}(val).(interface{ Validate() error }); ok {
				if err := v.Validate(); err != nil {
					return ClusterLoadAssignmentValidationError{
						field:  fmt.Sprintf("NamedEndpoints[%v]", key),
						reason: "embedded message failed validation",
						cause:  err,
					}
				}
			}

		}
	}

	if all {
		switch v := interface{}(m.GetPolicy()).(type) {
		case interface{ ValidateAll() error }:
			if err := v.ValidateAll(); err != nil {
				errors = append(errors, ClusterLoadAssignmentValidationError{
					field:  "Policy",
					reason: "embedded message failed validation",
					cause:  err,
				})
			}
		case interface{ Validate() error }:
			if err := v.Validate(); err != nil {
				errors = append(errors, ClusterLoadAssignmentValidationError{
					field:  "Policy",
					reason: "embedded message failed validation",
					cause:  err,
				})
			}
		}
	} else if v, ok := interface{}(m.GetPolicy()).(interface{ Validate() error }); ok {
		if err := v.Validate(); err != nil {
			return ClusterLoadAssignmentValidationError{
				field:  "Policy",
				reason: "embedded message failed validation",
				cause:  err,
			}
		}
	}

	if len(errors) > 0 {
		return ClusterLoadAssignmentMultiError(errors)
	}
	return nil
}

// ClusterLoadAssignmentMultiError is an error wrapping multiple validation
// errors returned by ClusterLoadAssignment.ValidateAll() if the designated
// constraints aren't met.
type ClusterLoadAssignmentMultiError []error

// Error returns a concatenation of all the error messages it wraps.
func (m ClusterLoadAssignmentMultiError) Error() string {
	var msgs []string
	for _, err := range m {
		msgs = append(msgs, err.Error())
	}
	return strings.Join(msgs, "; ")
}

// AllErrors returns a list of validation violation errors.
func (m ClusterLoadAssignmentMultiError) AllErrors() []error { return m }

// ClusterLoadAssignmentValidationError is the validation error returned by
// ClusterLoadAssignment.Validate if the designated constraints aren't met.
type ClusterLoadAssignmentValidationError struct {
	field  string
	reason string
	cause  error
	key    bool
}

// Field function returns field value.
func (e ClusterLoadAssignmentValidationError) Field() string { return e.field }

// Reason function returns reason value.
func (e ClusterLoadAssignmentValidationError) Reason() string { return e.reason }

// Cause function returns cause value.
func (e ClusterLoadAssignmentValidationError) Cause() error { return e.cause }

// Key function returns key value.
func (e ClusterLoadAssignmentValidationError) Key() bool { return e.key }

// ErrorName returns error name.
func (e ClusterLoadAssignmentValidationError) ErrorName() string {
	return "ClusterLoadAssignmentValidationError"
}

// Error satisfies the builtin error interface
func (e ClusterLoadAssignmentValidationError) Error() string {
	cause := ""
	if e.cause != nil {
		cause = fmt.Sprintf(" | caused by: %v", e.cause)
	}

	key := ""
	if e.key {
		key = "key for "
	}

	return fmt.Sprintf(
		"invalid %sClusterLoadAssignment.%s: %s%s",
		key,
		e.field,
		e.reason,
		cause)
}

var _ error = ClusterLoadAssignmentValidationError{}

var _ interface {
	Field() string
	Reason() string
	Key() bool
	Cause() error
	ErrorName() string
} = ClusterLoadAssignmentValidationError{}

// Validate checks the field values on ClusterLoadAssignment_Policy with the
// rules defined in the proto definition for this message. If any rules are
// violated, the first error encountered is returned, or nil if there are no violations.
func (m *ClusterLoadAssignment_Policy) Validate() error {
	return m.validate(false)
}

// ValidateAll checks the field values on ClusterLoadAssignment_Policy with the
// rules defined in the proto definition for this message. If any rules are
// violated, the result is a list of violation errors wrapped in
// ClusterLoadAssignment_PolicyMultiError, or nil if none found.
func (m *ClusterLoadAssignment_Policy) ValidateAll() error {
	return m.validate(true)
}

func (m *ClusterLoadAssignment_Policy) validate(all bool) error {
	if m == nil {
		return nil
	}

	var errors []error

	for idx, item := range m.GetDropOverloads() {
		_, _ = idx, item

		if all {
			switch v := interface{}(item).(type) {
			case interface{ ValidateAll() error }:
				if err := v.ValidateAll(); err != nil {
					errors = append(errors, ClusterLoadAssignment_PolicyValidationError{
						field:  fmt.Sprintf("DropOverloads[%v]", idx),
						reason: "embedded message failed validation",
						cause:  err,
					})
				}
			case interface{ Validate() error }:
				if err := v.Validate(); err != nil {
					errors = append(errors, ClusterLoadAssignment_PolicyValidationError{
						field:  fmt.Sprintf("DropOverloads[%v]", idx),
						reason: "embedded message failed validation",
						cause:  err,
					})
				}
			}
		} else if v, ok := interface{}(item).(interface{ Validate() error }); ok {
			if err := v.Validate(); err != nil {
				return ClusterLoadAssignment_PolicyValidationError{
					field:  fmt.Sprintf("DropOverloads[%v]", idx),
					reason: "embedded message failed validation",
					cause:  err,
				}
			}
		}

	}

	if wrapper := m.GetOverprovisioningFactor(); wrapper != nil {

		if wrapper.GetValue() <= 0 {
			err := ClusterLoadAssignment_PolicyValidationError{
				field:  "OverprovisioningFactor",
				reason: "value must be greater than 0",
			}
			if !all {
				return err
			}
			errors = append(errors, err)
		}

	}

	if d := m.GetEndpointStaleAfter(); d != nil {
		dur, err := d.AsDuration(), d.CheckValid()
		if err != nil {
			err = ClusterLoadAssignment_PolicyValidationError{
				field:  "EndpointStaleAfter",
				reason: "value is not a valid duration",
				cause:  err,
			}
			if !all {
				return err
			}
			errors = append(errors, err)
		} else {

			gt := time.Duration(0*time.Second + 0*time.Nanosecond)

			if dur <= gt {
				err := ClusterLoadAssignment_PolicyValidationError{
					field:  "EndpointStaleAfter",
					reason: "value must be greater than 0s",
				}
				if !all {
					return err
				}
				errors = append(errors, err)
			}

		}
	}

	// no validation rules for DisableOverprovisioning

	if len(errors) > 0 {
		return ClusterLoadAssignment_PolicyMultiError(errors)
	}
	return nil
}

// ClusterLoadAssignment_PolicyMultiError is an error wrapping multiple
// validation errors returned by ClusterLoadAssignment_Policy.ValidateAll() if
// the designated constraints aren't met.
type ClusterLoadAssignment_PolicyMultiError []error

// Error returns a concatenation of all the error messages it wraps.
func (m ClusterLoadAssignment_PolicyMultiError) Error() string {
	var msgs []string
	for _, err := range m {
		msgs = append(msgs, err.Error())
	}
	return strings.Join(msgs, "; ")
}

// AllErrors returns a list of validation violation errors.
func (m ClusterLoadAssignment_PolicyMultiError) AllErrors() []error { return m }

// ClusterLoadAssignment_PolicyValidationError is the validation error returned
// by ClusterLoadAssignment_Policy.Validate if the designated constraints
// aren't met.
type ClusterLoadAssignment_PolicyValidationError struct {
	field  string
	reason string
	cause  error
	key    bool
}

// Field function returns field value.
func (e ClusterLoadAssignment_PolicyValidationError) Field() string { return e.field }

// Reason function returns reason value.
func (e ClusterLoadAssignment_PolicyValidationError) Reason() string { return e.reason }

// Cause function returns cause value.
func (e ClusterLoadAssignment_PolicyValidationError) Cause() error { return e.cause }

// Key function returns key value.
func (e ClusterLoadAssignment_PolicyValidationError) Key() bool { return e.key }

// ErrorName returns error name.
func (e ClusterLoadAssignment_PolicyValidationError) ErrorName() string {
	return "ClusterLoadAssignment_PolicyValidationError"
}

// Error satisfies the builtin error interface
func (e ClusterLoadAssignment_PolicyValidationError) Error() string {
	cause := ""
	if e.cause != nil {
		cause = fmt.Sprintf(" | caused by: %v", e.cause)
	}

	key := ""
	if e.key {
		key = "key for "
	}

	return fmt.Sprintf(
		"invalid %sClusterLoadAssignment_Policy.%s: %s%s",
		key,
		e.field,
		e.reason,
		cause)
}

var _ error = ClusterLoadAssignment_PolicyValidationError{}

var _ interface {
	Field() string
	Reason() string
	Key() bool
	Cause() error
	ErrorName() string
} = ClusterLoadAssignment_PolicyValidationError{}

// Validate checks the field values on
// ClusterLoadAssignment_Policy_DropOverload with the rules defined in the
// proto definition for this message. If any rules are violated, the first
// error encountered is returned, or nil if there are no violations.
func (m *ClusterLoadAssignment_Policy_DropOverload) Validate() error {
	return m.validate(false)
}

// ValidateAll checks the field values on
// ClusterLoadAssignment_Policy_DropOverload with the rules defined in the
// proto definition for this message. If any rules are violated, the result is
// a list of violation errors wrapped in
// ClusterLoadAssignment_Policy_DropOverloadMultiError, or nil if none found.
func (m *ClusterLoadAssignment_Policy_DropOverload) ValidateAll() error {
	return m.validate(true)
}

func (m *ClusterLoadAssignment_Policy_DropOverload) validate(all bool) error {
	if m == nil {
		return nil
	}

	var errors []error

	if len(m.GetCategory()) < 1 {
		err := ClusterLoadAssignment_Policy_DropOverloadValidationError{
			field:  "Category",
			reason: "value length must be at least 1 bytes",
		}
		if !all {
			return err
		}
		errors = append(errors, err)
	}

	if all {
		switch v := interface{}(m.GetDropPercentage()).(type) {
		case interface{ ValidateAll() error }:
			if err := v.ValidateAll(); err != nil {
				errors = append(errors, ClusterLoadAssignment_Policy_DropOverloadValidationError{
					field:  "DropPercentage",
					reason: "embedded message failed validation",
					cause:  err,
				})
			}
		case interface{ Validate() error }:
			if err := v.Validate(); err != nil {
				errors = append(errors, ClusterLoadAssignment_Policy_DropOverloadValidationError{
					field:  "DropPercentage",
					reason: "embedded message failed validation",
					cause:  err,
				})
			}
		}
	} else if v, ok := interface{}(m.GetDropPercentage()).(interface{ Validate() error }); ok {
		if err := v.Validate(); err != nil {
			return ClusterLoadAssignment_Policy_DropOverloadValidationError{
				field:  "DropPercentage",
				reason: "embedded message failed validation",
				cause:  err,
			}
		}
	}

	if len(errors) > 0 {
		return ClusterLoadAssignment_Policy_DropOverloadMultiError(errors)
	}
	return nil
}

// ClusterLoadAssignment_Policy_DropOverloadMultiError is an error wrapping
// multiple validation errors returned by
// ClusterLoadAssignment_Policy_DropOverload.ValidateAll() if the designated
// constraints aren't met.
type ClusterLoadAssignment_Policy_DropOverloadMultiError []error

// Error returns a concatenation of all the error messages it wraps.
func (m ClusterLoadAssignment_Policy_DropOverloadMultiError) Error() string {
	var msgs []string
	for _, err := range m {
		msgs = append(msgs, err.Error())
	}
	return strings.Join(msgs, "; ")
}

// AllErrors returns a list of validation violation errors.
func (m ClusterLoadAssignment_Policy_DropOverloadMultiError) AllErrors() []error { return m }

// ClusterLoadAssignment_Policy_DropOverloadValidationError is the validation
// error returned by ClusterLoadAssignment_Policy_DropOverload.Validate if the
// designated constraints aren't met.
type ClusterLoadAssignment_Policy_DropOverloadValidationError struct {
	field  string
	reason string
	cause  error
	key    bool
}

// Field function returns field value.
func (e ClusterLoadAssignment_Policy_DropOverloadValidationError) Field() string { return e.field }

// Reason function returns reason value.
func (e ClusterLoadAssignment_Policy_DropOverloadValidationError) Reason() string { return e.reason }

// Cause function returns cause value.
func (e ClusterLoadAssignment_Policy_DropOverloadValidationError) Cause() error { return e.cause }

// Key function returns key value.
func (e ClusterLoadAssignment_Policy_DropOverloadValidationError) Key() bool { return e.key }

// ErrorName returns error name.
func (e ClusterLoadAssignment_Policy_DropOverloadValidationError) ErrorName() string {
	return "ClusterLoadAssignment_Policy_DropOverloadValidationError"
}

// Error satisfies the builtin error interface
func (e ClusterLoadAssignment_Policy_DropOverloadValidationError) Error() string {
	cause := ""
	if e.cause != nil {
		cause = fmt.Sprintf(" | caused by: %v", e.cause)
	}

	key := ""
	if e.key {
		key = "key for "
	}

	return fmt.Sprintf(
		"invalid %sClusterLoadAssignment_Policy_DropOverload.%s: %s%s",
		key,
		e.field,
		e.reason,
		cause)
}

var _ error = ClusterLoadAssignment_Policy_DropOverloadValidationError{}

var _ interface {
	Field() string
	Reason() string
	Key() bool
	Cause() error
	ErrorName() string
} = ClusterLoadAssignment_Policy_DropOverloadValidationError{}
