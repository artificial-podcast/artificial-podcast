package texts

import (
	"context"
	"io/ioutil"

	texttospeech "cloud.google.com/go/texttospeech/apiv1"
	texttospeechpb "google.golang.org/genproto/googleapis/cloud/texttospeech/v1"
)

const (
	FEMALE int = iota
	MALE
)

func SynthesizeSSML(content, outputFile, languageName, languageCode string, gender int) error {
	ctx := context.Background()

	client, err := texttospeech.NewClient(ctx)
	if err != nil {
		return err
	}
	defer client.Close()

	voiceGender := texttospeechpb.SsmlVoiceGender_NEUTRAL
	if gender == FEMALE {
		voiceGender = texttospeechpb.SsmlVoiceGender_FEMALE
	} else {
		voiceGender = texttospeechpb.SsmlVoiceGender_MALE
	}

	req := texttospeechpb.SynthesizeSpeechRequest{
		Input: &texttospeechpb.SynthesisInput{
			InputSource: &texttospeechpb.SynthesisInput_Ssml{Ssml: content},
		},
		Voice: &texttospeechpb.VoiceSelectionParams{
			Name:         languageName,
			LanguageCode: languageCode,
			SsmlGender:   voiceGender,
		},
		AudioConfig: &texttospeechpb.AudioConfig{
			AudioEncoding: texttospeechpb.AudioEncoding_MP3,
		},
	}

	resp, err := client.SynthesizeSpeech(ctx, &req)
	if err != nil {
		return err
	}

	err = ioutil.WriteFile(outputFile, resp.AudioContent, 0644)
	if err != nil {
		return err
	}
	return nil
}
