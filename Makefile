TARGET_LINUX = GOARCH=amd64 GOOS=linux

.PHONY: cli
cli:
	cd cmd/cli && go build -o ap main.go && mv ap ${GOPATH}/bin/ap
	cd cmd/crawler && go build -o apc main.go && mv apc ${GOPATH}/bin/apc

