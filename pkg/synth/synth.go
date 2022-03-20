package synth

import (
	"context"
	"io/ioutil"
	"os"
	"strings"
)

const (
	defaultSynthTimeout = 300 // sec i.e. 5min
)

type Voice string

func SynthesizeSSML(ctx context.Context, source, output string, voice Voice, remove bool) error {
	ssml, err := ioutil.ReadFile(source)
	if err != nil {
		return err
	}

	out, err := os.Create(output)
	if err != nil {
		return err
	}
	defer out.Close()

	err = SynthesizeWithPolly(ctx, string(ssml), out, voice.PollyVoice(), remove, defaultSynthTimeout)
	if err != nil {
		out.Close()
		os.Remove(output) // best effort, don't care about any errors at this point

		return err
	}

	return nil
}

func VoiceId(voice string) Voice {
	switch strings.ToLower(string(voice)) {
	case "joanna":
		return "joanna"
	case "amy":
		return "amy"
	}
	return "amy"
}
