package synth

import (
	"context"
	"io/ioutil"
	"os"
)

type (
	Voice string
)

func SynthesizeSSML(ctx context.Context, source, output string, voice Voice) error {
	ssml, err := ioutil.ReadFile(source)
	if err != nil {
		return err
	}

	out, err := os.Create(output)
	if err != nil {
		return nil
	}
	defer out.Close()

	return SynthesizeWithPolly(ctx, string(ssml), out, voice)
}
