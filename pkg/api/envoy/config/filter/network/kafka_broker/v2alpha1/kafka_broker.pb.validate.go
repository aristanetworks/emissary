// Code generated by protoc-gen-validate. DO NOT EDIT.
// source: envoy/config/filter/network/kafka_broker/v2alpha1/kafka_broker.proto

package v2alpha1

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

// Validate checks the field values on KafkaBroker with the rules defined in
// the proto definition for this message. If any rules are violated, the first
// error encountered is returned, or nil if there are no violations.
func (m *KafkaBroker) Validate() error {
	return m.validate(false)
}

// ValidateAll checks the field values on KafkaBroker with the rules defined in
// the proto definition for this message. If any rules are violated, the
// result is a list of violation errors wrapped in KafkaBrokerMultiError, or
// nil if none found.
func (m *KafkaBroker) ValidateAll() error {
	return m.validate(true)
}

func (m *KafkaBroker) validate(all bool) error {
	if m == nil {
		return nil
	}

	var errors []error

	if len(m.GetStatPrefix()) < 1 {
		err := KafkaBrokerValidationError{
			field:  "StatPrefix",
			reason: "value length must be at least 1 bytes",
		}
		if !all {
			return err
		}
		errors = append(errors, err)
	}

	if len(errors) > 0 {
		return KafkaBrokerMultiError(errors)
	}
	return nil
}

// KafkaBrokerMultiError is an error wrapping multiple validation errors
// returned by KafkaBroker.ValidateAll() if the designated constraints aren't met.
type KafkaBrokerMultiError []error

// Error returns a concatenation of all the error messages it wraps.
func (m KafkaBrokerMultiError) Error() string {
	var msgs []string
	for _, err := range m {
		msgs = append(msgs, err.Error())
	}
	return strings.Join(msgs, "; ")
}

// AllErrors returns a list of validation violation errors.
func (m KafkaBrokerMultiError) AllErrors() []error { return m }

// KafkaBrokerValidationError is the validation error returned by
// KafkaBroker.Validate if the designated constraints aren't met.
type KafkaBrokerValidationError struct {
	field  string
	reason string
	cause  error
	key    bool
}

// Field function returns field value.
func (e KafkaBrokerValidationError) Field() string { return e.field }

// Reason function returns reason value.
func (e KafkaBrokerValidationError) Reason() string { return e.reason }

// Cause function returns cause value.
func (e KafkaBrokerValidationError) Cause() error { return e.cause }

// Key function returns key value.
func (e KafkaBrokerValidationError) Key() bool { return e.key }

// ErrorName returns error name.
func (e KafkaBrokerValidationError) ErrorName() string { return "KafkaBrokerValidationError" }

// Error satisfies the builtin error interface
func (e KafkaBrokerValidationError) Error() string {
	cause := ""
	if e.cause != nil {
		cause = fmt.Sprintf(" | caused by: %v", e.cause)
	}

	key := ""
	if e.key {
		key = "key for "
	}

	return fmt.Sprintf(
		"invalid %sKafkaBroker.%s: %s%s",
		key,
		e.field,
		e.reason,
		cause)
}

var _ error = KafkaBrokerValidationError{}

var _ interface {
	Field() string
	Reason() string
	Key() bool
	Cause() error
	ErrorName() string
} = KafkaBrokerValidationError{}
