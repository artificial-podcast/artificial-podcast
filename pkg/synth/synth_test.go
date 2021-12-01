package synth

import (
	"context"
	"io/ioutil"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

const (
	source = "../../examples/texts/text1.txt"
	output = "../../examples/texts/text1.mp3"
)

func TestSynthesizeWithPolly(t *testing.T) {
	ssml, err := ioutil.ReadFile(source)
	assert.NoError(t, err)

	out, err := os.Create(output)
	assert.NoError(t, err)
	defer out.Close()

	ctx := context.Background()
	err = SynthesizeWithPolly(ctx, string(ssml), out, "Joanna", 120)
	assert.NoError(t, err)
}

func TestSynthesizeWithPollyTimeout(t *testing.T) {
	ssml, err := ioutil.ReadFile(source)
	assert.NoError(t, err)

	out, err := os.Create(output)
	assert.NoError(t, err)
	defer out.Close()

	ctx := context.Background()
	err = SynthesizeWithPolly(ctx, string(ssml), out, "Joanna", 20) // usually takes ca 30-32 sec ...
	assert.NoError(t, err)
}
