# This file deals with Emissary's (non-tool) dependencies.
# (tool dependencies are in tools.mk)

go-mod-tidy:
.PHONY: go-mod-tidy

go-mod-tidy: go-mod-tidy/main
go-mod-tidy/main: $(OSS_HOME)/build-aux/go-version.txt
	rm -f go.sum
	GOFLAGS=-mod=mod go mod tidy -compat=$$(cut -d. -f1,2 < $<) -go=$$(cut -d. -f1,2 < $<)
.PHONY: go-mod-tidy/main

vendor: FORCE
	go mod vendor
clean: vendor.rm-r


$(OSS_HOME)/build-aux/go-version.txt: $(_go-version/deps)
	$(_go-version/cmd) > $@
clean: build-aux/go-version.txt.rm

$(OSS_HOME)/build-aux/py-version.txt: $(OSS_HOME)/build-aux/Dockerfile
	{ grep -o 'python:3\.[0-9]*' | head -1 | cut -d: -f2; } < $< > $@
clean: build-aux/py-version.txt.rm

$(OSS_HOME)/build-aux/go1%.src.tar.gz:
	curl -o $@ --fail -L https://dl.google.com/go/$(@F)
build-aux/go.src.tar.gz.clean:
	rm -f build-aux/go1*.src.tar.gz
clobber: build-aux/go.src.tar.gz.clean
