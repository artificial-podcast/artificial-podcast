package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"os"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/polly"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

const (
	defaultBucketName = "artificial-podcast-generate"
	defaultRegion     = "eu-central-1"
)

var (
	s3Client    *s3.Client
	pollyClient *polly.Client
)

func init() {
	ctx := context.TODO()

	// generic config foo
	cfg, err := config.LoadDefaultConfig(ctx, config.WithRegion(defaultRegion))
	if err != nil {
		log.Fatalf("unable to load AWS config, %v", err)
	}

	s3Client = s3.NewFromConfig(cfg)
	if s3Client == nil {
		log.Fatal("unable to create client for AWS S3")
	}

	pollyClient = polly.NewFromConfig(cfg)
	if pollyClient == nil {
		log.Fatal("unable to create client for AWS Polly")
	}
}

func main() {
	var bucket string
	var filename string

	flag.StringVar(&bucket, "b", defaultBucketName, "The bucket to upload the file to")
	flag.StringVar(&filename, "f", "", "The file to upload")
	flag.Parse()

	ctx := context.TODO()

	file, err := os.Open(filename)
	if err != nil {
		log.Fatalf("unable to open file, %v", err)
	}
	defer file.Close()

	uploadInput := &s3.PutObjectInput{
		Bucket: &bucket,
		Key:    &filename,
		Body:   file,
	}
	_, err = s3Client.PutObject(ctx, uploadInput)
	if err != nil {
		log.Fatalf("unable to upload file, %v", err)
	}

	synthesisTaskInput := &polly.StartSpeechSynthesisTaskInput{
		OutputFormat: ,
	}
	synthesisTaskResult, err := pollyClient.StartSpeechSynthesisTask(ctx, synthesisTaskInput)
	if err != nil {
		log.Fatalf("error starting speech synthesis task, %v", err)
	}

	fmt.Println(synthesisTaskResult)
}
