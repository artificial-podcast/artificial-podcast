TARGET_LINUX = GOARCH=amd64 GOOS=linux

.PHONY: cli
cli:
	cd cmd/ssml2mp3 && go build -o ssml2mp3 main.go && mv ssml2mp3 ${GOPATH}/bin/ssml2mp3
	cd cmd/txt2ssml && go build -o txt2ssml main.go && mv txt2ssml ${GOPATH}/bin/txt2ssml
