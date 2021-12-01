package synth

import (
	"context"
	"fmt"
	"io"
	"log"
	"time"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/polly"
	"github.com/aws/aws-sdk-go-v2/service/polly/types"
	"github.com/aws/aws-sdk-go-v2/service/s3"

	"github.com/txsvc/stdlib/pkg/env"
)

const (
	defaultInputBucketName  = "artificial-podcast-generate"
	defaultOutputBucketName = "artificial-podcast-audio"
	defaultRegion           = "eu-central-1"
	pollRate                = 20 // seconds
)

var (
	s3Client    *s3.Client
	pollyClient *polly.Client

	outputBucketName = env.GetString("ARTIFICIAL_PODCAST_BUCKET", defaultOutputBucketName)
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

func (Voice) PollyVoiceId() types.VoiceId {
	return types.VoiceIdJoanna
}

func SynthesizeWithPolly(ctx context.Context, ssml string, dst io.Writer, voice Voice, timeout int) error {
	ctx, cancel := context.WithTimeout(ctx, time.Duration(timeout)*time.Second)
	defer cancel()

	ssmlText := string(ssml)
	synthesisTaskInput := &polly.StartSpeechSynthesisTaskInput{
		VoiceId:            voice.PollyVoiceId(),
		OutputS3BucketName: &outputBucketName,
		OutputFormat:       types.OutputFormatMp3,
		Engine:             types.EngineNeural,
		TextType:           types.TextTypeSsml,
		Text:               &ssmlText,
	}

	synthesisTaskResult, err := pollyClient.StartSpeechSynthesisTask(ctx, synthesisTaskInput)
	if err != nil {
		return err
	}
	taskId := *synthesisTaskResult.SynthesisTask.TaskId

	// wait for the audio file to be come available
	found := false
	audioFile := fmt.Sprintf("%s.mp3", taskId)
	listObjectsInput := &s3.ListObjectsV2Input{
		Bucket: &outputBucketName,
	}

	for !found {
		resp, err := s3Client.ListObjectsV2(ctx, listObjectsInput)
		if err != nil {
			return err
		}
		for _, item := range resp.Contents {
			key := *item.Key
			if key == audioFile {
				found = true
			}
		}

		if !found {
			select {
			case <-ctx.Done():
				return ctx.Err()
			default:
				time.Sleep(pollRate * time.Second)
			}
		}
	}

	// audio file is ready
	getObjectInput := &s3.GetObjectInput{
		Bucket: &outputBucketName,
		Key:    &audioFile,
	}
	resp, err := s3Client.GetObject(ctx, getObjectInput)
	if err != nil {
		return err
	}

	if _, err := io.Copy(dst, resp.Body); err != nil {
		return err
	}

	return nil
}
