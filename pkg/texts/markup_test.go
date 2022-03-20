package texts

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

const (
	source = "../../examples/texts/text1.md"
	output = "../../examples/texts/text1.ssml"
)

func TestMarkupText(t *testing.T) {
	err := MarkupText(source, output, true)
	assert.NoError(t, err)
}
