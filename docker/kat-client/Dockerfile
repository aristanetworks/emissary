# syntax = docker/dockerfile:1.3

FROM golang:1.23.3-alpine3.20 as builder

WORKDIR /build

# Copy Go module files
COPY go.mod go.sum ./
COPY vendor vendor

# Copy required source code
COPY cmd/kat-client cmd/kat-client
COPY pkg pkg
COPY api api

# Build the binary
RUN --mount=type=cache,target=/root/.cache/go-build \
    go build -mod=vendor -trimpath -o /kat-client ./cmd/kat-client

FROM alpine:3.20

WORKDIR /work

# Copy the binary
COPY --from=builder /kat-client /work/kat-client

# Sleep by default (for testing)
CMD ["sleep", "3600"]
