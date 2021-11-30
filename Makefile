TARGET_LINUX = GOARCH=amd64 GOOS=linux


.PHONY: cli
cli:
	cd cmd/text2mp3 && go build -o text2mp3 main.go && mv text2mp3 ${GOPATH}/bin/text2mp3
